"""
Глобальный rate limiter приложения.

Создаётся в одном месте, чтобы middleware в main.py и декораторы
в роутерах использовали один и тот же экземпляр — иначе состояние
счётчиков не разделяется и лимиты работают непредсказуемо.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)