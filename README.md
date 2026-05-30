# 🎓 MyAppCourses — Платформа для микрообучения

Бэкенд REST API сервиса онлайн-обучения с возможностью покупать и проходить курсы.

## 📋 Описание

Сервис реализует платформу микрообучения с тремя уровнями доступа:

- **Неавторизованный пользователь** — просмотр каталога курсов
- **Авторизованный пользователь** — доступ к бесплатным пробным темам
- **Пользователь, купивший курс** — полный доступ ко всем темам курса

Проект выполнен в рамках итоговой работы по дисциплине  
«Разработка веб-сервисов и приложений (бэкенд)».

## ✨ Возможности

### Основной функционал
- 🔐 Регистрация и аутентификация через JWT (access + refresh токены)
- 👥 Роли пользователей (user / admin)
- 📚 Полный CRUD курсов, категорий, тем
- 💳 Покупка курсов
- ❤️ Лайки курсов
- 🎯 Гибкий доступ к контенту (бесплатные темы / только для купивших)

### Дополнительные возможности
- 🔍 **Поиск** курсов по названию и описанию (`?search=python`)
- 🗂️ **Фильтрация** по категории (`?category_id=1`)
- 📊 **Сортировка** по дате/цене/названию (`?sort_by=price&order=asc`)
- 📄 **Пагинация** (`?skip=0&limit=20`)
- 🔥 **Популярные курсы** — топ по количеству лайков (`/courses/popular`)
- 🚦 **Rate limiting** — защита от брутфорса на эндпоинтах auth (slowapi)
- 📝 **Структурированное логирование** всех HTTP-запросов (loguru)
- 📧 **Email-уведомления** при регистрации и покупке (заглушки, готовы к интеграции SMTP)
- 🤖 **CI/CD** через GitHub Actions — автозапуск тестов при каждом push
- 🎨 **Линтер ruff** для контроля качества кода

## 🛠 Стек технологий

| Категория | Технология |
|---|---|
| Язык | Python 3.12 |
| Фреймворк | FastAPI (async) |
| ORM | SQLAlchemy 2.0 (async) |
| База данных | PostgreSQL 16 |
| Миграции | Alembic |
| Валидация | Pydantic v2 |
| Аутентификация | JWT (access + refresh) |
| Хеширование паролей | bcrypt (passlib) |
| Тестирование | Pytest, pytest-asyncio, httpx |
| Контейнеризация | Docker, Docker Compose |
| Веб-сервер | Uvicorn |
| Логирование | Loguru |
| Rate limiting | SlowAPI |
| Линтер | Ruff |
| CI/CD | GitHub Actions |


## 🚀 Быстрый запуск (Docker)

### Требования

- Docker
- Docker Compose

### Шаги

```bash
# 1. Клонировать репозиторий
git clone <url-вашего-репозитория>
cd MyAppCourses

# 2. Создать .env из примера
cp .env.example .env

# 3. Поднять контейнеры (PostgreSQL + приложение)
docker-compose up --build
```

После запуска приложение автоматически:
- дождётся готовности PostgreSQL,
- применит миграции Alembic,
- запустит FastAPI на порту **8000**.

### Доступные адреса

| Назначение | URL |
|---|---|
| Swagger UI (интерактивная документация) | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health-check | http://localhost:8000/health |

### Остановка

```bash
docker-compose down            # остановить контейнеры
docker-compose down -v         # + удалить данные БД (volume)
```


## ⚙️ Переменные окружения

Файл `.env` в корне проекта. Пример — в `.env.example`.

| Переменная | Назначение | Пример |
|---|---|---|
| `POSTGRES_USER` | Пользователь PostgreSQL | `postgres` |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL | `postgres` |
| `POSTGRES_DB` | Имя базы данных | `courses_db` |
| `POSTGRES_HOST` | Хост БД (в Docker — имя сервиса) | `db` |
| `POSTGRES_PORT` | Порт БД | `5432` |
| `DATABASE_URL` | Полный async URL подключения | `postgresql+asyncpg://postgres:postgres@db:5432/courses_db` |
| `JWT_SECRET_KEY` | Секрет для подписи JWT | `super-secret-key-change-me` |
| `JWT_ALGORITHM` | Алгоритм подписи | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни access-токена (мин) | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Время жизни refresh-токена (дн) | `7` |


> ⚠️ **Важно:** в продакшене обязательно смените `JWT_SECRET_KEY` и пароли БД.


## 🗄️ Миграции базы данных (Alembic)

Миграции применяются **автоматически** при запуске Docker-контейнера приложения.

### Ручное управление (внутри контейнера)

```bash
# Войти в контейнер приложения
docker-compose exec app bash

# Применить все миграции
alembic upgrade head

# Откатить последнюю миграцию
alembic downgrade -1

# Создать новую миграцию (после изменения моделей)
alembic revision --autogenerate -m "описание изменений"

# Посмотреть текущую версию
alembic current

# История миграций
alembic history
```

### Локальный запуск (без Docker)

```bash
# Установить зависимости
pip install -r requirements.txt

# Применить миграции
alembic upgrade head
```



## 📡 API Endpoints

Полная интерактивная документация: **http://localhost:8000/docs**

### 🔐 Аутентификация (`/auth`)

| Метод | Endpoint | Описание | Auth |
|---|---|---|---|
| `POST` | `/auth/register` | Регистрация нового пользователя | ❌ |
| `POST` | `/auth/login` | Вход (получение access + refresh токенов) | ❌ |
| `POST` | `/auth/refresh` | Обновление access-токена по refresh | ❌ |
| `POST` | `/auth/logout` | Выход (отзыв refresh-токена) | ✅ |

### 👤 Пользователи (`/users`)

| Метод | Endpoint | Описание | Auth |
|---|---|---|---|
| `GET` | `/users/me` | Профиль текущего пользователя | ✅ |
| `PATCH` | `/users/me` | Обновить свой профиль | ✅ |
| `GET` | `/users/{user_id}` | Получить пользователя по ID | ✅ |

### 🗂 Категории (`/categories`)

| Метод | Endpoint | Описание | Auth |
|---|---|---|---|
| `GET` | `/categories` | Список всех категорий | ❌ |
| `GET` | `/categories/{category_id}` | Детали категории | ❌ |
| `POST` | `/categories` | Создать категорию | ✅ (admin) |
| `PATCH` | `/categories/{category_id}` | Обновить категорию | ✅ (admin) |
| `DELETE` | `/categories/{category_id}` | Удалить категорию | ✅ (admin) |

### 📚 Курсы (`/courses`)

| Метод | Endpoint | Описание | Auth |
|---|---|---|---|
| `GET` | `/courses` | Список курсов с фильтрами, поиском, сортировкой, пагинацией | ❌ |
| `GET` | `/courses/popular` | Топ популярных курсов (по лайкам) | ❌ |
| `GET` | `/courses/{course_id}` | Детали курса | ❌ |
| `POST` | `/courses` | Создать курс | ✅ (admin) |
| `PATCH` | `/courses/{course_id}` | Обновить курс | ✅ (admin) |
| `DELETE` | `/courses/{course_id}` | Удалить курс | ✅ (admin) |

**Query-параметры для `GET /courses`:**
- `category_id` — фильтр по ID категории
- `search` — поиск по названию и описанию (регистронезависимый)
- `sort_by` — `created_at` / `price` / `title` (по умолчанию `created_at`)
- `order` — `asc` / `desc` (по умолчанию `desc`)
- `skip` — смещение для пагинации (по умолчанию `0`)
- `limit` — количество на страницу, 1-100 (по умолчанию `20`)

### 📝 Темы курса (`/topics`)

> Темы — это уроки/модули внутри курса.  
> Доступ к теме зависит от флага `is_free` и наличия покупки курса.

| Метод | Endpoint | Описание | Auth |
|---|---|---|---|
| `GET` | `/courses/{course_id}/topics` | Список тем курса | ❌ |
| `GET` | `/topics/{topic_id}` | Получить тему (контент доступен по правам) | ⚠️ см. ниже |
| `POST` | `/courses/{course_id}/topics` | Создать тему | ✅ (owner) |
| `PATCH` | `/topics/{topic_id}` | Обновить тему | ✅ (owner) |
| `DELETE` | `/topics/{topic_id}` | Удалить тему | ✅ (owner) |

**Правила доступа к контенту темы:**
- 🌍 Гость → видит только список тем (без контента)
- 🔓 Авторизованный → видит контент тем с `is_free=true`
- 💎 Купивший курс → видит контент всех тем

### 💳 Покупки (`/purchases`)

| Метод | Endpoint | Описание | Auth |
|---|---|---|---|
| `POST` | `/courses/{course_id}/purchase` | Купить курс | ✅ |
| `GET` | `/users/me/purchases` | Список моих покупок | ✅ |
| `GET` | `/purchases/{purchase_id}` | Детали покупки | ✅ (owner) |

### ❤️ Лайки (`/likes`)

| Метод | Endpoint | Описание | Auth |
|---|---|---|---|
| `POST` | `/courses/{course_id}/like` | Поставить лайк курсу | ✅ |
| `DELETE` | `/courses/{course_id}/like` | Убрать лайк | ✅ |
| `GET` | `/courses/{course_id}/likes` | Количество лайков курса | ❌ |

### ❤️‍🩹 Health-check

| Метод | Endpoint | Описание |
|---|---|---|
| `GET` | `/health` | Проверка работоспособности сервиса |


## 📂 Структура проекта

```
MyAppCourses/
├── alembic/                        # Миграции БД
│   └── versions/                   # Файлы миграций
├── app/
│   ├── core/                       # Ядро приложения
│   │   ├── config.py               # Настройки (Pydantic Settings)
│   │   ├── database.py             # AsyncSession, engine, Base
│   │   ├── exceptions.py           # Кастомные исключения
│   │   └── security.py             # JWT, хеширование паролей
│   │
│   ├── crud/                       # Операции с БД (низкий уровень)
│   │   ├── category.py
│   │   ├── course.py
│   │   ├── like.py
│   │   ├── purchase.py
│   │   ├── topic.py
│   │   └── user.py
│   │
│   ├── dependencies/               # FastAPI Depends (auth, roles, db)
│   │
│   ├── models/                     # SQLAlchemy ORM-модели
│   │
│   ├── routers/                    # Роутеры (API endpoints)
│   │   ├── auth.py                 # /auth — регистрация, логин, refresh
│   │   ├── category.py             # /categories — категории курсов
│   │   ├── course.py               # /courses — CRUD курсов
│   │   ├── like.py                 # /likes — лайки курсов
│   │   ├── purchase.py             # /purchases — покупки курсов
│   │   ├── topic.py                # /topics — темы курсов
│   │   └── user.py                 # /users — профили
│   │
│   ├── schemas/                    # Pydantic-схемы (валидация I/O)
│   │   ├── auth.py
│   │   ├── category.py
│   │   ├── course.py
│   │   ├── like.py
│   │   ├── purchase.py
│   │   ├── topic.py
│   │   └── user.py
│   │
│   ├── services/                   # Бизнес-логика
│   │   ├── auth_service.py
│   │   ├── category_service.py
│   │   ├── course_service.py
│   │   ├── like_service.py
│   │   ├── purchase_service.py
│   │   ├── topic_service.py
│   │   └── user_service.py
│   │
│   └── main.py                     # Точка входа FastAPI
│
├── tests/                          # Тесты
│   ├── api/                        # Тесты API-слоя
│   │   └── test_health.py
│   ├── integration/                # Интеграционные тесты
│   │   ├── test_auth.py
│   │   ├── test_auth_password.py
│   │   ├── test_auth_refresh.py
│   │   ├── test_categories.py
│   │   ├── test_course_detail.py
│   │   ├── test_courses.py
│   │   ├── test_likes.py
│   │   ├── test_purchases.py
│   │   ├── test_topics.py
│   │   └── test_users.py
│   ├── unit/                       # Юнит-тесты
│   │   ├── test_exceptions.py
│   │   └── test_security.py
│   └── conftest.py                 # Фикстуры pytest
│
├── htmlcov/                        # HTML-отчёт покрытия тестами
├── .env.example                    # Пример переменных окружения
├── .dockerignore
├── .gitignore
├── alembic.ini                     # Конфиг Alembic
├── docker-compose.yml              # Описание сервисов (app + db)
├── Dockerfile                      # Образ приложения
├── requirements.txt                # Python-зависимости
└── README.md
```

### Архитектура слоёв

Проект построен по принципу **слоистой архитектуры**:

```
routers (API)  →  services (бизнес-логика)  →  crud (работа с БД)  →  models (ORM)
                            ↓
                      schemas (Pydantic-валидация)
```

- **`routers/`** — принимают HTTP-запросы, валидируют через `schemas/`, вызывают `services/`
- **`services/`** — содержат бизнес-логику (проверки прав, оркестрация)
- **`crud/`** — низкоуровневые операции с БД (SELECT/INSERT/UPDATE/DELETE)
- **`models/`** — SQLAlchemy-модели таблиц
- **`schemas/`** — Pydantic-схемы для валидации входа/выхода
- **`core/`** — конфиг, безопасность, исключения, подключение к БД
- **`dependencies/`** — общие зависимости FastAPI (получение текущего пользователя и т.д.)


## 🧪 Тестирование

Проект покрыт **юнит-** и **интеграционными** тестами на `pytest` + `pytest-asyncio` + `httpx`.

### Структура тестов

```
tests/
├── unit/             # Юнит-тесты (security, exceptions)
├── integration/      # Интеграционные тесты API (auth, courses, topics, ...)
├── api/              # Базовые проверки (health-check)
└── conftest.py       # Общие фикстуры (test client, test DB, тестовый юзер)
```

### Запуск тестов

#### В Docker

```bash
# Запустить все тесты внутри контейнера
docker-compose exec app pytest

# С подробным выводом
docker-compose exec app pytest -v

# Только юнит-тесты
docker-compose exec app pytest tests/unit

# Только интеграционные
docker-compose exec app pytest tests/integration

# Конкретный файл
docker-compose exec app pytest tests/integration/test_auth.py

# Конкретный тест
docker-compose exec app pytest tests/integration/test_auth.py::test_register_success
```

#### Локально

```bash
# Установить зависимости
pip install -r requirements.txt

# Запустить тесты
pytest -v
```

### Покрытие кода (coverage)

```bash
# Запустить тесты с измерением покрытия
pytest --cov=app --cov-report=term-missing

# Сгенерировать HTML-отчёт
pytest --cov=app --cov-report=html

# Открыть отчёт
# Windows:
start htmlcov/index.html
# Linux/Mac:
open htmlcov/index.html
```

HTML-отчёт сохраняется в папке `htmlcov/` и показывает построчное покрытие.

### Что покрыто тестами

✅ Регистрация и логин пользователей  
✅ Обновление access-токена по refresh  
✅ Смена и валидация паролей  
✅ CRUD категорий и курсов  
✅ Получение детальной информации о курсе  
✅ Управление темами курса (`topics`)  
✅ Покупка курса и доступ к платному контенту  
✅ Лайки курсов  
✅ Управление пользователями  
✅ Кастомные исключения и хеширование паролей (unit)


## 👨‍💻 Автор

Проект выполнен в рамках итоговой работы по дисциплине  
**«Разработка веб-сервисов и приложений (бэкенд)»**.

- 🎓 Автор: *Волкова Анна Дмитриевна>*
- 🏫 Группа: *ПСиАПР-24*
- 📅 Год: 2026