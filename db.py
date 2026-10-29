"""
Модуль для работы с PostgreSQL базой данных.
Асинхронные функции для получения и изменения данных.
"""
import psycopg
from psycopg.rows import dict_row
import logging

logger = logging.getLogger(__name__)

# Настройки подключения к БД
DB_CONFIG = {
    "dbname": "DetectiveCards",
    "user": "Sarkred",
    "password": "7YskhYBxHAN4g",  # ⚠️ ЗАМЕНИ НА СВОЙ ПАРОЛЬ
    "host": "cnpg-dccards-rw",
    "port": "5432"
}


async def get_db_connection():
    """Создает и возвращает асинхронное подключение к БД."""
    return await psycopg.AsyncConnection.connect(**DB_CONFIG)


# ===== ФУНКЦИИ ДЛЯ ПОЛУЧЕНИЯ ДАННЫХ =====

async def get_user(user_id: str) -> dict | None:
    """
    Получает данные пользователя по ID.
    Возвращает словарь с данными или None, если пользователь не найден.
    """
    conn = await get_db_connection()
    try:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            user = await cur.fetchone()
            
            if user:
                # Получаем список карт пользователя
                await cur.execute(
                    "SELECT card_id FROM user_inventory WHERE user_id = %s", 
                    (user_id,)
                )
                cards = [row['card_id'] for row in await cur.fetchall()]
                user['cards'] = cards
            
            return user
    finally:
        await conn.close()


async def get_user_cards(user_id: str) -> list:
    """Получает список ID карт пользователя."""
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT card_id FROM user_inventory WHERE user_id = %s", 
                (user_id,)
            )
            rows = await cur.fetchall()
            return [row[0] for row in rows]
    finally:
        await conn.close()


async def get_card(card_id: int) -> dict | None:
    """Получает данные карты по ID."""
    conn = await get_db_connection()
    try:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute("SELECT * FROM cards WHERE card_id = %s", (card_id,))
            return await cur.fetchone()
    finally:
        await conn.close()


# ===== ФУНКЦИИ ДЛЯ ИЗМЕНЕНИЯ ДАННЫХ =====

async def update_user_cents(user_id: str, new_cents: int):
    """Обновляет баланс бэт-коинов у пользователя."""
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE users SET cents = %s WHERE user_id = %s", 
                (new_cents, user_id)
            )
            await conn.commit()
    finally:
        await conn.close()


async def add_card_to_user(user_id: str, card_id: int):
    """Добавляет карту в инвентарь пользователя."""
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO user_inventory (user_id, card_id) VALUES (%s, %s)", 
                (user_id, card_id)
            )
            await conn.commit()
    finally:
        await conn.close()


async def remove_card_from_user(user_id: str, card_id: int):
    """Удаляет одну карту из инвентаря пользователя."""
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                "DELETE FROM user_inventory WHERE user_id = %s AND card_id = %s "
                "LIMIT 1", 
                (user_id, card_id)
            )
            await conn.commit()
    finally:
        await conn.close()


async def update_user_free_rolls(user_id: str, new_rolls: int):
    """Обновляет количество бесплатных попыток."""
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE users SET free_rolls = %s WHERE user_id = %s", 
                (new_rolls, user_id)
            )
            await conn.commit()
    finally:
        await conn.close()


async def update_user_field(user_id: str, field: str, value):
    """
    Универсальная функция для обновления любого поля пользователя.
    Например: update_user_field(user_id, "casino_attempts", 5)
    """
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cur:
            # Используем параметризацию для защиты от SQL-инъекций
            await cur.execute(
                f"UPDATE users SET {field} = %s WHERE user_id = %s", 
                (value, user_id)
            )
            await conn.commit()
    finally:
        await conn.close()


async def create_user_if_not_exists(user_id: str, username: str = None, first_name: str = None):
    """Создает нового пользователя, если его ещё нет в базе."""
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cur:
            await cur.execute("""
                INSERT INTO users (user_id, username, first_name, cents, free_rolls, 
                                   casino_attempts, quests_data, darkest_night)
                VALUES (%s, %s, %s, 0, 0, 5, '{}', '{}')
                ON CONFLICT (user_id) DO NOTHING
            """, (user_id, username, first_name))
            await conn.commit()
    finally:
        await conn.close()
