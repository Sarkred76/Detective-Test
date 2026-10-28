import psycopg
from psycopg.rows import dict_row

# Настройки подключения
DB_CONFIG = {
    "dbname": "DetectiveCards",
    "user": "Sarkred",
    "password": "7YskhYBxHAN4g",  # ⚠️ Вставь пароль
    "host": "cnpg-dccards-rw",
    "port": "5432"
}

async def get_db_connection():
    """Создает и возвращает асинхронное подключение."""
    return await psycopg.AsyncConnection.connect(**DB_CONFIG)

# ===== ФУНКЦИИ ДЛЯ ПОЛУЧЕНИЯ ДАННЫХ =====

async def get_user(user_id: str) -> dict:
    """Получает данные пользователя по ID."""
    conn = await get_db_connection()
    try:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            user = await cur.fetchone()
            return user  # Вернет словарь или None, если не найден
    finally:
        await conn.close()

async def get_user_cards(user_id: str) -> list:
    """Получает список ID карт пользователя."""
    conn = await get_db_connection()
    try:
        async with conn.cursor() as cur:
            await cur.execute("SELECT card_id FROM user_inventory WHERE user_id = %s", (user_id,))
            rows = await cur.fetchall()
            return [row[0] for row in rows]
    finally:
        await conn.close()

# ===== ФУНКЦИИ ДЛЯ ИЗМЕНЕНИЯ ДАННЫХ =====

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

async def update_user_cents(user_id: str, new_cents: int):
    """Обновляет баланс бэт-коинов."""
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
