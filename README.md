# praktikum_new_diplom

# "Продуктовый помощник" (Foodgram)

## 1. [Описание](#1)
## 2. [База данных и переменные окружения](#2)
## 3. [Команды для запуска](#3)
## 4. [Заполнение базы данных](#4)
## 5. [Техническая информация](#5)
## 6. [Об авторе](#6)

---
## 1. Описание <a id=1></a>
"Продуктовый помощник" - платформа, где пользователи могут делиться друг с другом рецептами блюд.

В проекте реализовано следующее:
  - аутентификация пользователей с использованием токенов
  - создание и редактирование рецептов
  - фильтрация рецептов по тегам
  - "Избранное" и "Корзина"
  - подписки на пользователей
  - загрузка списка покупок, созданного на основе рецепетов из "Корзины"

---

## 2. База данных и переменные окружения <a id=2></a>

Проект использует базу данных PostgreSQL.  
Для подключения и выполненя запросов к базе данных необходимо создать и заполнить файл ".env" с переменными окружения в папке "./infra/".

Шаблон для заполнения файла ".env":
```python
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

---
## 3. Команды для запуска <a id=3></a>

Перед запуском необходимо склонировать проект:
```bash
HTTPS: git clone https://github.com/CeaPanochka/foodgram-project-react.git
SSH: git clone git@github.com:CeaPanochka/foodgram-project-react.git
```

Cоздать и активировать виртуальное окружение:
```bash
python -m venv venv
```
```bash
Linux: source venv/bin/activate
Windows: source venv/Scripts/activate
```
#### Для работы локально
Перейти в папку и установить зависимости из файла requirements.txt:
```bash
cd foodgram-project-react/backend/foodgram/
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```
#### Запуск в docker
Необходимо собрать образы для фронтенда и бэкенда.  
Из папки "./backend/foodgram/" выполнить команду:
```bash
docker build -t foodgram_backend .
```

Из папки "./frontend/" выполнить команду:
```bash
docker build -t foodgram_frontend .
```

После создания образов можно создавать и запускать контейнеры.  
Из папки "./infra/" выполнить команду:
```bash
docker-compose up -d
```

После успешного запуска контейнеров выполнить миграции:
```bash
docker-compose exec web python manage.py migrate
```

Создать суперюзера (Администратора):
```bash
docker-compose exec web python manage.py createsuperuser
```

Собрать статику:
```bash
docker-compose exec web python manage.py collectstatic --no-input
```

Теперь доступность проекта можно проверить по адресу [http://localhost/](http://localhost/)

---
## 4. Заполнение базы данных <a id=4></a>

С проектом поставляются данные об ингредиентах.  
Заполнить базу данных ингредиентами можно выполнив следующую команду из папки "./infra/":
```bash
docker-compose exec web python manage.py loaddata ingredients.json
```
или
```bash
docker-compose exec web python manage.py fill_ingredients_from_csv --path data/
```

Также необходимо заполнить базу данных тегами.  
Для этого необходимо войти в [админ-зону](http://localhost/admin/)
проекта под логином и паролем администратора (пользователя, созданного командой createsuperuser).

---
## 5. Техническая информация <a id=5></a>

Стек технологий: Python 3, Django, DRF, React, Docker, PostgreSQL, nginx, gunicorn, Djoser.

Веб-сервер: nginx (контейнер nginx)  
Frontend фреймворк: React (контейнер frontend)  
Backend фреймворк: Django (контейнер web)  
API фреймворк: DRF (контейнер web)  
База данных: PostgreSQL (контейнер db)

Веб-сервер nginx перенаправляет запросы клиентов к контейнерам frontend и web, либо к хранилищам (volume) статики и файлов.  
Контейнер nginx взаимодействует с контейнером web через gunicorn.  
Контейнер frontend взаимодействует с контейнером web посредством API-запросов.

---
## 6. Об авторе <a id=6></a>

Цыбулаев Дмитрий Андреевич  
Python-разработчик (Backend)  
Россия, г. Москва 
E-mail: titampeach@gmail.com 
Telegram: @mititam
