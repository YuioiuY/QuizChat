import aiosqlite, asyncio


class DatabaseExplorer():
    def __init__(self):
        self.db = None
        self.DB_NAME = 'source/quiz_bot.db'
        self.init = False

    async def my_cursor(self, request, *args):
        async with aiosqlite.connect(self.DB_NAME) as db:
            async with db.execute(request, args[0] if len(args) == 1 and isinstance(args[0], tuple) else args) as cursor:
                if request.strip().lower().startswith("select"):
                    results = await cursor.fetchall()
                    if results:
                        return results[0][0]
                    return None
                else:
                    await db.commit()  # Не забывайте коммит для команд `INSERT`, `UPDATE`, `DELETE`
                    return None
                

    #region encryption
    def encrypt_to_hex(self,input_string):
        return ''.join(format(ord(char), '02x') for char in input_string)


    def decrypt_from_hex(self,hex_string):
        return ''.join(chr(int(hex_string[i:i+2], 16)) for i in range(0, len(hex_string), 2))

    #endregion 

    #region Database initialization    
    def initialize(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.create_table())
        self.init = True


    async def create_table(self):
        async with aiosqlite.connect('source/quiz_bot.db') as db:

            await db.execute('''CREATE TABLE IF NOT EXISTS users_score (user_id INTEGER PRIMARY KEY, user STRING, score INTEGER, quiz_id INTEGER, question_number INTEGER)''')
            await db.commit()

            await db.execute('''CREATE TABLE IF NOT EXISTS quiz_question (key INTEGER PRIMARY KEY, quiz_key INTEGER, quiz_name STRING, question_number INTEGER, question STRING, answers STRING, correct_answer STRING)''')
            await db.commit()
    #endregion

    #region quiz manipulate functions for create new quiz            
    async def get_quiz_key_by_name(self, quiz_name):
        return await self.my_cursor('SELECT quiz_key FROM quiz_question WHERE quiz_name = (?)', (quiz_name, ))
        
                
    async def get_last_quiz_key(self):
        return await self.my_cursor('SELECT quiz_key FROM quiz_question ORDER BY quiz_key DESC LIMIT 1')
        
                
    async def get_last_key(self):
        return await self.my_cursor('SELECT MAX(key) FROM quiz_question')
        
    #endregion
    
    #region Create Quiz Question
    async def create_quiz(self,dict_quiz):
        quiz_key = await self.get_quiz_key_by_name(dict_quiz['name'])
        name = dict_quiz['name']
        dict_quiz.pop('name')
        if quiz_key is None:
            quiz_key = await self.get_last_quiz_key()
            if quiz_key is None:
                quiz_key = 1
            else:
                quiz_key = quiz_key[0] + 1
            async with aiosqlite.connect(self.DB_NAME) as db:
                for quiz in dict_quiz:
                    key = await self.get_last_key()

                    if key[0] is None:
                        key = 1
                    else:
                        key = key[0] + 1

                    await db.execute('INSERT INTO quiz_question (key, quiz_key, quiz_name, question_number, question, answers, correct_answer) VALUES (?, ?, ?, ?, ?, ?, ?)',
                                      (key, quiz_key, name, quiz, dict_quiz[quiz][0], f'{dict_quiz[quiz][1]}', dict_quiz[quiz][2]))
                    await db.commit()
    #endregion
    
    #region Get question, answers 
    async def get_quizzes(self):
        async with aiosqlite.connect(self.DB_NAME) as db:
            async with db.execute('SELECT DISTINCT quiz_name FROM quiz_question') as cursor:
                quizzes = await cursor.fetchall()
                return [quiz[0] for quiz in quizzes]
    
    async def get_question(self, quiz_name, question_number):
        return await self.my_cursor('SELECT question FROM quiz_question WHERE quiz_name = (?) AND question_number = (?)', (quiz_name, question_number,))
    
    async def get_question_number(self, name):
        return await self.my_cursor('SELECT question_number FROM users_score WHERE user = (?)', (self.encrypt_to_hex(name), ))

    async def get_question_answers(self, quiz_name, question_number):
        return await self.my_cursor('SELECT answers FROM quiz_question WHERE quiz_name = (?) AND question_number = (?)', (quiz_name, question_number,))
        
    async def get_question_correct_answer(self, quiz_name, question_number):
        return await self.my_cursor('SELECT correct_answer FROM quiz_question WHERE quiz_name = (?) AND question_number = (?)', (quiz_name, question_number,))
    #endregion

    #region Update User Table

    async def update_user(self, name, score, quiz_key, question_number):
        await self.my_cursor('UPDATE users_score SET score = (?), quiz_id = (?), question_number = (?) WHERE user = (?)',(score, quiz_key, question_number, self.encrypt_to_hex(name)))

    async def get_last_user_id(self):
        return await self.my_cursor('SELECT MAX(user_id) FROM users_score')
    
    async def get_user_by_name(self, name):
        return await self.my_cursor('SELECT user_id FROM users_score WHERE user = (?)', (self.encrypt_to_hex(name), ))
    

    async def get_my_score(self, name):
        return await self.my_cursor('SELECT score FROM users_score WHERE user = (?)', (self.encrypt_to_hex(name), ))


    async def create_user(self, name):
        user_id = await self.get_user_by_name(name)
        if user_id is None:
            user_id = await self.get_last_user_id()
            
            if user_id is None or user_id[0] is None:
                user_id = 1
            else:
                user_id = user_id[0] + 1
            name = self.encrypt_to_hex(name)
            await self.my_cursor('INSERT INTO users_score (user_id, user, score, quiz_id, question_number) VALUES (?, ?, ?, ?, ?)', 
                                 (user_id, name, 0, 0, 0,))
        
    #endregion

