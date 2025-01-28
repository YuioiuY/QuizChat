from DBWorker import DatabaseExplorer
from create_qiuz import CreateQuiz

db = DatabaseExplorer()
db.initialize()

if db.init == True:
    quiz = CreateQuiz(db)
    quiz.Create()
else:
    print("DatabaseExplorer Error: DatabaseExplorer is not initialized")

