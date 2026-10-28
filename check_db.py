import psycopg

# Твои данные для подключения (те же, что в migrate_data.py)
DB_CONFIG = {
    "dbname": "DetectiveCards",
    "user": "Sarkred",
    "password": "7YskhYBxHAN4g",  # ⚠️ Вставь пароль
    "host": "cnpg-dccards-rw",
    "port": "5432"
}

def check():
    print("🔌 Подключение к базе...")
    try:
        conn = psycopg.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 1. Считаем количество записей в таблицах
        tables = ['users', 'cards', 'user_inventory', 'clans', 'clan_members']
        print("\n📊 Статистика базы данных:")
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"  • Таблица {table}: {count} записей")
            
        # 2. Проверяем конкретного пользователя (например, первого из JSON)
        cur.execute("SELECT user_id, username, cents FROM users LIMIT 1")
        user = cur.fetchone()
        if user:
            print(f"\n👤 Пример пользователя из БД:")
            print(f"  • ID: {user[0]}")
            print(f"  • Username: {user[1]}")
            print(f"  • Баланс: {user[2]} бэт-коинов")
            
            # 3. Проверяем его инвентарь
            cur.execute("SELECT COUNT(*) FROM user_inventory WHERE user_id = %s", (user[0],))
            inv_count = cur.fetchone()[0]
            print(f"  • Карт в инвентаре: {inv_count} шт.")
        
        cur.close()
        conn.close()
        print("\n✅ База данных работает отлично!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    check()
