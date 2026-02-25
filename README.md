## Ready4VPR

Backend-платформа для онлайн-обучения.
Реализует управление курсами и уроками, подписки, систему платежей через Stripe, разграничение ролей, фоновые задачи 
и автоматизированный деплой.

Проект построен на Django + DRF и разворачивается в Docker-инфраструктуре с CI/CD через GitHub Actions.

### Архитектура

Django + Django REST Framework

PostgreSQL

Redis

Celery + Celery Beat

Stripe API

Gunicorn

Nginx

Docker / Docker Compose

GitHub Actions (CI/CD)

### Пользователи и роли

**Пользователь**

- Регистрация через API

- Управление своим профилем

- Просмотр курсов и уроков

- Подписка на обновления курса

- Оплата курсов и уроков

- Просмотр своих платежей

**Модератор**

- Просмотр и редактирование курсов

- Контроль контента

- Доступ к платежам пользователей

**Суперпользователь**

- Полный доступ ко всем данным

**Реализованы кастомные permissions**

- IsOwner

- IsModerator

- IsProfileOwner

- Комбинированные права через DRF

### Курсы и уроки

**Курсы**

- CRUD через ViewSet

- Автоматическое назначение владельца

- Подписки пользователей

- Подсчёт количества уроков

- Отправка email при обновлении курса (если обновление произошло спустя 4+ часа)

**Уроки**

- CRUD через APIView

- Привязка к курсу

- Ограничение на сторонние видео-ссылки (разрешён только YouTube)

- Пагинация

- Валидатор видео: разрешены только домены:

    - youtube.com
    
    - youtu.be

### Платежи (Stripe)

**Реализована интеграция с Stripe:**

1. Создание платежа

- Создаётся продукт в Stripe

- Создаётся цена

- Создаётся Checkout Session

- Возвращается:

    - payment_id
    
    - checkout_url
    
    - payment_amount

2. Проверка статуса платежа

- Отдельный endpoint возвращает:

    - статус оплаты
    
    - статус сессии
    
    - итоговую сумму
    
    - валюту

Платеж может относиться либо к курсу, либо к уроку (валидация на уровне модели и сериализатора).

### Подписки и уведомления

**Подписка на курс**

- Endpoint добавляет или удаляет подписку

- Уникальность (user, course)

**Email-уведомления**

- При обновлении курса подписчикам отправляется письмо.

**Celery-задачи:**

- send_course_update_email (сообщение пользователю об обновлении куса, на который он подписан)

- block_nonactive_user (блокировка пользователей без активности > 30 дней)

### Пользователи

- Кастомная модель пользователя (email как USERNAME_FIELD)

- Аватар

- Город

- Номер телефона

- Prefetch платежей в профиле

- Админ-панель кастомизирована:

    - Превью аватара
    
    - Расширенные поля

### API Эндпоинты (основные)
```
Пользователи

POST /users/register/

GET /users/

GET /users/{id}/

PATCH /users/{id}/

Курсы

GET /courses/

POST /courses/

GET /courses/{id}/

PATCH /courses/{id}/

DELETE /courses/{id}/

Уроки

GET /lessons/

POST /lessons/

GET /lessons/{id}/

PATCH /lessons/{id}/

DELETE /lessons/{id}/

Подписки

POST /courses/subscribe/

Платежи

POST /payments/create/

GET /payments/

GET /payments/{id}/

GET /payments/status/{payment_id}/
```

### Переменные окружения

- .env не коммитится в репозиторий.

- Основные переменные:

````
DJANGO_SECRET_KEY=your_secret_key_here
DEBUG=False

DB_NAME=your_database_name_here
DB_USER=your_database_user_here
DB_HOST=db
DB_PORT=5432
DB_PASSWORD=your_database_password_here

REDIS_LOCATION=redis://redis:6379/1
CELERY_BROKER_URL=redis://redis:6379/2
CELERY_RESULT_BACKEND=redis://redis:6379/3

EMAIL_HOST_USER=your_email_host_user_here
EMAIL_HOST_PASSWORD=your_email_host_password_here
EMAIL_HOST=smtp.yandex.ru
EMAIL_PORT=465
EMAIL_USE_TLS=False
EMAIL_USE_SSL=True

STRIPE_API_KEY=your_api_stripe_key_here

DOCKER_HUB_USERNAME=your_docker_hub_username_here
DOCKER_HUB_TAG=docker_hub_ready_four_vpr_image_tag_here

BASE_SERVER_URL=localhost
````

### Настройка удалённого сервера

**На сервере должны быть установлены:**
````
sudo apt update
sudo apt install -y docker.io docker-compose-plugin nginx
````

**Дополнительно:**

- пользователь добавлен в группу docker

- вход по SSH-ключу

- открыты порты 80, 443, 22

- проект размещается в директории:
/home/<user>/ready4vpr

### GitHub Secrets

В репозитории → Settings → Secrets and variables → Actions должны быть добавлены:

| Secret                    | Назначение              |
| ------------------------- | ----------------------- |
| `DJANGO_SECRET_KEY`       | Django SECRET_KEY       |
| `DB_PASSWORD`             | Пароль PostgreSQL       |
| `EMAIL_HOST_USER`         | Почта                   |
| `EMAIL_HOST_PASSWORD`     | Пароль почты            |
| `STRIPE_API_KEY`          | Stripe API key          |
| `BASE_SERVER_URL`         | Домен или IP сервера    |
| `DOCKER_HUB_USERNAME`     | Docker Hub username     |
| `DOCKER_HUB_ACCESS_TOKEN` | Docker Hub access token |
| `SSH_KEY`                 | Приватный SSH-ключ      |
| `SSH_USER`                | Пользователь сервера    |
| `SERVER_IP`               | IP сервера              |

### Docker-инфраструктура

- Проект запускается через Docker Compose:

web (Django + Gunicorn)

db (PostgreSQL)

redis

celery

celery-beat

nginx


### CI/CD (GitHub Actions)

Workflow включает:

- Lint

    - flake8

- Tests

    - Django tests

- Build

    - сборка Docker image

    - push в Docker Hub

- Deploy

    - генерация .env
    
    - деплой на сервер через SSH
    
    - docker compose pull
    
    - docker compose up -d

Workflow запускается автоматически при каждом push.

### Развёртывание

**Локально**
```
git clone https://github.com/nadezhdapopova-spec/Ready4VPR
cd ready4vpr
docker compose up --build
```

На сервере:
```
cd ~/ready4vpr
docker compose pull
docker compose up -d
```

### Production-особенности

- Custom User model

- Stripe integration

- Role-based permissions

- Object-level access control

- Celery background tasks

- Redis caching

- Dockerized infrastructure

- CI/CD pipeline

- Email notifications

- Prefetch/select_related оптимизация

- Pagination

- DRF filtering & ordering


### Автор

Надежда Попова

Python Backend Developer