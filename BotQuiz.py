from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from crypt4crypr import Crypt
from source.DBWorker import DatabaseExplorer
import asyncio, logging

#region Init and load
my_crypt = Crypt()
db = DatabaseExplorer()
db.initialize()
logging.basicConfig(level=logging.INFO)
API_TOKEN = my_crypt.token_Factory()
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
#endregion 

class QuizStates(StatesGroup):
    choosing_quiz = State()
    answering_question = State()

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await db.create_user(message.from_user.username)
    
    markup = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='Начать игру')]],
        resize_keyboard=True
    )
    await message.answer("Добро пожаловать в викторину!", reply_markup=markup)


@dp.message(lambda message: message.text == 'Начать игру')
async def start_quiz(message: types.Message, state: FSMContext):
    
    quizzes = await db.get_quizzes()  
    keyboard = []
    for quiz in quizzes:
        keyboard.append([KeyboardButton(text=quiz)])

    markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    
    await message.answer("Выберите викторину:", reply_markup=markup)
    await state.set_state(QuizStates.choosing_quiz)

@dp.message(QuizStates.choosing_quiz)
async def choose_quiz(message: types.Message, state: FSMContext):
    quiz_name = message.text
    quiz_key = await db.get_quiz_key_by_name(quiz_name)
    
    if quiz_key:
        await state.update_data(quiz_name=quiz_name, quiz_key=quiz_key, question_number=1)
        await send_question(message, state)
    else:
        await message.answer("Викторина не найдена. Попробуйте еще раз.")

async def send_question(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data['question_number'] > 10:
        markup = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text='Начать игру')]],
            resize_keyboard=True
        )
        score = await db.get_my_score(message.from_user.username)
        await message.answer("Викторина завершена! Ваш счет: " + str(score) + "", reply_markup=markup)
        await state.clear()
        return
    
    quiz_name = user_data['quiz_name']
    question_number = user_data['question_number']
    question = await db.get_question(quiz_name, question_number)
    answers = eval(await db.get_question_answers(quiz_name, question_number))
    
    if question and answers:
        keyboard = []
        for answer in answers:
            keyboard.append([KeyboardButton(text=answer)])
        markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
        
        
        await message.answer(question, reply_markup=markup)
        await state.set_state(QuizStates.answering_question)
    else:
        await message.answer("Викторина завершена!", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Начать игру')))
        await state.clear()


@dp.message(QuizStates.answering_question)
async def answer_question(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    quiz_name = user_data['quiz_name']
    quiz_key = user_data['quiz_key']
    question_number = user_data['question_number']
    username = message.from_user.username
    correct_answer = await db.get_question_correct_answer(quiz_name, question_number)
    
    if message.text == str(correct_answer):
        await message.answer("Правильно!")
        current_score = await db.get_my_score(username)
        await db.update_user(username, current_score + 1, quiz_key, question_number + 1)
    else:
        await message.answer(f"Неправильно! Правильный ответ: {correct_answer}")
        await db.update_user(username, await db.get_my_score(username), quiz_key, question_number + 1)
    
    await state.update_data(question_number=question_number + 1)
    await send_question(message, state)

async def main():
    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    asyncio.run(main())