# Ready4VPR
Django проект для отслеживания курсов и обучения с Celery задачами и Redis.

## Быстрый старт с Docker Compose

1. #### GitHub: **клонируй репозиторий**
````
bash
git clone https://github.com/nadezhdapopova-spec/Ready4VPR/
cd Ready4VPR
````
2. **Создай файл .env**

Скопируй .env.sample или создай .env с твоими настройками:
````
SECRET_KEY=your_secret_key_here
DEBUG=True

DB_NAME=your_database_name_here
DB_USER=your_database_user_here
DB_PASSWORD=your_database_password_here
DB_HOST=db
DB_PORT=5432

LOCATION=redis://redis:6379/1

CELERY_BROKER_URL=redis://redis:6379/2
CELERY_RESULT_BACKEND=redis://redis:6379/3

STRIPE_API_KEY=your_api_stripe_key_here

EMAIL_HOST=smtp.yandex.ru
EMAIL_PORT=465
EMAIL_USE_TLS=False
EMAIL_USE_SSL=True
EMAIL_HOST_USER=your_email_host_user_here
EMAIL_HOST_PASSWORD=your_email_host_password_here
````
3. **Запуск проекта**
````
bash
docker compose up --build

Или в фоне:
bash
docker compose up -d --build
````
Первый запуск займёт ~2-3 минуты (сборка образа + миграции)

4. **Проверка работоспособности**

| Сервис        | Статус                | Команда проверки                | Ожидаемый результат         |
| ------------- | --------------------- | ------------------------------- | --------------------------- |
| Django Web    | http://localhost:8000 | Открой в браузере               | Главная страница проекта    |
| PostgreSQL    | healthy               | docker compose ps               | Статус (healthy) у db       |
| Redis         | Up                    | docker compose logs redis       | Ready to accept connections |
| Celery Worker | Up                    | docker compose logs celery      | celery@... ready.           |
| Celery Beat   | Up                    | docker compose logs celery-beat | beat: Starting...           |

Быстрая проверка:
````
bash
docker compose ps
````
Все контейнеры должны быть Up (db — healthy).

| Действие                     | Команда                                                |
| ---------------------------- | ------------------------------------------------------ |
| Запуск                       | docker compose up --build                              |
| Запуск в фоне                | docker compose up -d --build                           |
| Остановка (с сохранением БД) | docker compose down                                    |
| Полная очистка (БД удалится) | docker compose down -v                                 |
| Логи конкретного сервиса     | docker compose logs web                                |
| Войти в контейнер            | docker compose exec web bash                           |

### Структура сервисов

## Структура сервисов

| Сервис       | Описание                          | Порт/Назначение          |
|--------------|-----------------------------------|--------------------------|
| **web**      | Django (runserver)                | `localhost:8000`         |
| **db**       | PostgreSQL 16                     | `db:5432`                |
| **redis**    | Redis (cache, Celery broker)      | `redis:6379`             |
| **celery**   | Celery worker (задачи)            | -                        |
| **celery-beat** | Celery scheduler (периодические задачи) | -                    |
