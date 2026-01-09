## Ready4VPR

Django-проект для отслеживания курсов и обучения.
Использует PostgreSQL, Redis, Celery, Celery beat, развёртывается на удалённом сервере с помощью Docker Compose и GitHub Actions.

### Архитектура

Django + DRF

PostgreSQL

Redis

Celery + Celery Beat

Gunicorn

Nginx

Docker / Docker Compose

GitHub Actions (CI/CD)

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

### Переменные окружения

**Файл .env:**

- не коммитится в репозиторий

- используется на сервере и создаётся автоматически в GitHub Actions

**Шаблон (.env.sample):**
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

### CI/CD (GitHub Actions)

Workflow расположен в .github/workflows/ci.yaml

**Алгоритм workflow:**
- Lint

    - запуск flake8


- Tests

    - запуск Django-тестов

    - при ошибках деплой останавливается


- Build

    - сборка Docker-образа

    - push в Docker Hub


- Deploy

    - генерация .env

    - подмена server_name в nginx.conf

    - деплой на сервер через rsync

    - загрузка образов сервисов, указанных в docker-compose.yaml (docker compose pull)

    - запуск сервисов в фоновом режиме (docker compose up -d)

Workflow запускается автоматически при каждом push.

### Деплой приложения

Деплой происходит автоматически после успешного прохождения тестов.

Ручной деплой на сервере:
````
cd ~/ready4vpr
docker compose pull
docker compose up -d
````