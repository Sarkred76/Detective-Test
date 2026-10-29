"""
Модуль для работы с PostgreSQL базой данных.
"""
import psycopg
from psycopg.rows import dict_row
import logging

logger = logging.getLogger(__name__)

# Настройки подключения к БД
DB_CONFIG = {
    "dbname": "DetectiveCards",
    "user": "Sarkred",
    "password": "7YskhYBxHAN4g",  # ⚠️ НЕ ЗАБУДЬ ВСТАВИТЬ ПАРОЛЬ
    "host": "cnpg-dccards-rw",
    "port": "5432"
}

async def get_db_connection():
    """Создает и возвращает асинхронное подключение к БД."""
    return await psycopg.AsyncConnection.connect(**DB_CONFIG)

# ===== ПОЛЬЗОВАТЕЛИ =====

async def get_user(user_id: str) -> dict | None:
    """Получает данные пользователя и его инвентарь."""
    conn = await get_db_connection()
    try:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            user = await cur.fetchone()
            
            if user:
                # Получаем список ID карт
                await cur.execute("SELECT card_id FROM user_inventory WHERE user_id = %s", (user_id,))
                cards = [row['card_id'] for row in await cur.fetchall()]
                user['cards'] = cards
            return user
    finally:
        await conn.close()

async def create_user_if_not_exists(user_id: str, username: str = None, first_name: str = None):
    """Создает нового пользователя, если его ещё нет."""
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

async def update_user_field(user_id: str, field: str, value):
    """Универсальное обновление поля пользователя."""
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cur:
            # Внимание: field не экранируется, передавай только проверенные имена полей!
            await cur.execute(f"UPDATE users SET {field} = %s WHERE user_id = %s", (value, user_id))
            await conn.commit()
    finally:
        await conn.close()

# ===== КАРТЫ (СПРАВОЧНИК) =====

async def get_all_cards() -> list:
    """Возвращает список всех карт из базы (аналог data['cards'])."""
    conn = await get_db_connection()
    try:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute("SELECT * FROM cards ORDER BY card_id")
            return await cur.fetchall()
    finally:
        await conn.close()

async def get_card(card_id: int) -> dict | None:
    """Находит одну карту по ID."""
    conn = await get_db_connection()
    try:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute("SELECT * FROM cards WHERE card_id = %s", (card_id,))
            return await cur.fetchone()
    finally:
        await conn.close()

# ===== ИНВЕНТАРЬ =====

async def add_card_to_user(user_id: str, card_id: int):
    """Добавляет карту в инвентарь."""
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cur:
            await cur.execute("INSERT INTO user_inventory (user_id, card_id) VALUES (%s, %s)", (user_id, card_id))
            await conn.commit()
    finally:
        await conn.close()

async def remove_card_from_user(user_id: str, card_id: int):
    """Удаляет одну копию карты из инвентаря."""
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM user_inventory WHERE user_id = %s AND card_id = %s LIMIT 1", (user_id, card_id))
            await conn.commit()
    finally:
        await conn.close()
