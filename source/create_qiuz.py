from DBWorker import DatabaseExplorer
import os,json, asyncio

class CreateQuiz:
    def __init__(self, db):
        self.PATH = 'source/quiz_base'
        self.data_list = []        
        self.db = db


    def Create(self):
        print("Create Local Quiz")
        for file_name in os.listdir(self.PATH):
            if file_name.endswith('.json'):  # Проверяем, что файл имеет расширение .json
                file_path = os.path.join(self.PATH, file_name)

                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)  
                        self.data_list.append(data) 
                    except json.JSONDecodeError as e:
                        print(f"Ошибка чтения файла {file_name}: {e}")

        asyncio.run(self.create_quiz())

    async def create_quiz(self):
        if self.db is not None:
            for data in self.data_list:
                await self.db.create_quiz(data)
                print(f'Created Quiz')






