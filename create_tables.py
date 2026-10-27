import psycopg

DB_CONFIG = {
    "dbname": "DetectiveCards",
    "user": "Sarkred",
    "password": "7dEd6iJx8d2_!TP",  # ⚠️ ЗАМЕНИ НА СВОЙ ПАРОЛЬ
    "host": "cnpg-dccards-rw",
    "port": "5432"
}

def create_tables():
    print("🔌 Подключение к базе данных...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("📖 Чтение файла create_tables.sql...")
        with open("create_tables.sql", "r", encoding="utf-8") as f:
            sql_script = f.read()
        
        print("⚙️ Выполнение скрипта создания таблиц...")
        cur.execute(sql_script)
        conn.commit()
        
        print("✅ Таблицы успешно созданы!")
        
        cur.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Ошибка базы данных: {e}")
    except FileNotFoundError:
        print("❌ Файл create_tables.sql не найден!")
    except Exception as e:
        print(f"❌ Неизвестная ошибка: {e}")

if __name__ == "__main__":
    create_tables()
