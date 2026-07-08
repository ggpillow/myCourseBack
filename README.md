# MyAppCourses — Backend for a Microlearning Platform

REST API for an online learning platform where users can browse, purchase, and access courses.

## 1. Features

- JWT authentication
- User roles (`user`, `admin`)
- CRUD for courses, categories, and topics
- Course purchase system
- Likes
- Search, filtering, sorting, and pagination
- Rate limiting
- Logging
- Automated tests

## 2. Tech Stack

- Python 3.12
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Pydantic
- Docker
- Pytest


## 3. Run

```bash
git clone <repo-url>
cd MyAppCourses
cp .env.example .env
docker compose up --build

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
## 4. Environment
### Environment Variables
The project uses a local `.env` file.  
Example values are provided in `.env.example`.

## 5. API Docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 6. Project Structure

app/
├── routers/
├── services/
├── crud/
├── models/
├── schemas/
└── core/

## 7. Testing
```bash
docker compose exec app pytest
```
## 8. Author
Anna Volkova
