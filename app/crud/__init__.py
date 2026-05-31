"""
Пакет CRUD-операций (Data Access Layer).

Каждый модуль содержит набор функций для работы с одной ORM-моделью:
get_by_id, create, update, delete и специфичные для сущности методы.
Функциональный стиль (без классов-обёрток) — современный FastAPI-подход,
обеспечивающий простоту, явность и удобство тестирования.

Слой CRUD изолирует SQL и ORM от бизнес-логики: сервисы работают с
этими функциями, не зная деталей запросов и связей в БД.
"""

from app.crud import category, course, like, purchase, topic, user

__all__ = ["user", "category", "course", "topic", "purchase", "like"]
