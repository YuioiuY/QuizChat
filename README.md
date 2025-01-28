# QuizChat

![alt text](https://github.com/YuioiuY/QuizChat/blob/main/source/images/logo.png)

## Как получить доступ ? 

Вы можете запустить бота на своей локальной машине или получить доступ по ссылке t.me/ChillQuizBot

## Библиотеки 
- aiogram 
- asyncio
- aiosqlite

## Особенности проекта 

В папке **source** вы найдете папку **quiz_base**, туда можно дополнительно загрузить квизы в формате *.json и пополнить библиотеку.
Для того что бы обновить базу данных, есть файл **rebuild_test.py** он позволить пополнить базу новыми квизами. 

Так же был написан отдельный обширный класс для работы с базой **sqlite**, для дальнейшего возможного расширения.

## Как он работает ? 

- Запуск по команде - **/start**.
- А дальше просто нажимаййте кнопки! 

![alt text](https://github.com/YuioiuY/QuizChat/blob/main/source/images/start.png)
![alt text](https://github.com/YuioiuY/QuizChat/blob/main/source/images/quizzes.png)
![alt text](https://github.com/YuioiuY/QuizChat/blob/main/source/images/end.png)

## Для удобства работы с базой

https://marketplace.visualstudio.com/items?itemName=qwtel.sqlite-viewer

