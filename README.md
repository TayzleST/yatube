# Yatube
[![Yatube%20workflow Actions Status](https://github.com/AlexanderNkn/yatube/workflows/Yatube%20workflow/badge.svg)](https://github.com/AlexanderNkn/yatube/actions)

Социальная сеть блогеров - учебный проект Яндекс.Практикум.

### Описание
Проект Yatube - это социальная сеть для публикации личных дневников. Сайт позволяет зарегистрированным пользователям публиковать тексты и добавлять к ним изображения, читать записи других пользователей, комментировать их и подписываться на понравившихся авторов. Так же пользователи могут создавать тематические группы и привязывать свои записи к таким группам. Можно посмотреть все записи связанные, с этой группой. Администратор может модерировать записи и блокировать пользователей.

### Стек
Сайт написан на Python с использованием Django, база данных на PostgreSQL. Вэб-интерфейс создан посредством Bootstrap. Добавление изображений через sorl-thumbnail. Проект покрыт тестами с использованием стандартной библиотеки unittest. Сайт развернут на сервисе Яндекс.Облако с использованием nginx и gunicorn. Ссылка на сайт https://blog-yatube.ml/ 

### Установка
- склонируйте проект с реппозитория GitHub, перейдите в директорию yatube, создайте виртуальное окружение и активируйте его
    ```
    git clone https://github.com/AlexanderNkn/yatube
    cd yatube/
    python3 -m venv venv && . venv/bin/activate
    ```
- установите зависимости
    ```
    pip install -r requirements.txt
    ```
- задайте пароль для django и выполните миграции и включите DEBUG для корректного отображения статики
    ```
    export SECRET_KEY=12345
    python manage.py makemigrations posts && python manage.py migrate
    export DEBUG=True
    ```
- запустите сервер и перейдите на страницу 127.0.0.1:8000
    ```
    python manage.py runserver
    ```
    
### Дополнительные возможности
- заполнить базу тестовыми данными
    ```
    python manage.py loaddata dump.json
    ```
- создать суперпользователя
    ```
    python manage.py createsuperuser
    ```
