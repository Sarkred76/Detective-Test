import json
import psycopg
import os

# Данные для подключения к БД на Amvera
DB_CONFIG = {
    "dbname": "DetectiveCards",
    "user": "Sarkred",
    "password": "7YskhYBxHAN4g",  # ⚠️ ЗАМЕНИ НА СВОЙ ПАРОЛЬ
    "host": "cnpg-dccards-rw",
    "port": "5432"
}

def migrate():
    print(" Чтение JSON файла...")
    
    # Путь к файлу данных на Amvera
    data_file = "/data/bot_data.json"
    
    if not os.path.exists(data_file):
        print(f"❌ Файл {data_file} не найден!")
        return
    
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print("🔌 Подключение к PostgreSQL...")
    conn = psycopg.connect(**DB_CONFIG, autocommit=False)
    cur = conn.cursor()
    
    # 1. Перенос карт
    print("🔄 Перенос карт...")
    cards_count = 0
    for card in data.get("cards", []):
        try:
            cur.execute("""
                INSERT INTO cards (card_id, title, rarity, image_url, file_id, media_type, available)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (card_id) DO NOTHING;
            """, (
                card["id"], 
                card["title"], 
                card["rarity"], 
                card.get("image_url"), 
                card.get("file_id"), 
                card.get("media_type", "photo"), 
                card.get("available", True)
            ))
            cards_count += 1
        except Exception as e:
            print(f"️ Ошибка при переносе карты {card.get('id')}: {e}")
    
    print(f"✅ Перенесено карт: {cards_count}")
    
    # 2. Перенос пользователей
    print("\n🔄 Перенос пользователей и инвентаря...")
    users_count = 0
    inventory_count = 0
    
    for user_id, udata in data.get("users", {}).items():
        try:
            quests_data = {
                "seasonal_quests": udata.get("seasonal_quests", {}),
                "daily_quests": udata.get("daily_quests", []),
                "weekly_quests": udata.get("weekly_quests", [])
            }
            darkest_night = udata.get("darkest_night", {})
            
            cur.execute("""
                INSERT INTO users (user_id, username, first_name, last_name, cents, free_rolls, 
                                   casino_attempts, last_casino_reset, avatar_url, quests_data, darkest_night)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO NOTHING;
            """, (
                user_id, 
                udata.get("username"), 
                udata.get("first_name"), 
                udata.get("last_name"),
                udata.get("cents", 0), 
                udata.get("free_rolls", 0),
                udata.get("casino_attempts", 5), 
                udata.get("last_casino_reset", 0),
                udata.get("avatar_url"), 
                json.dumps(quests_data), 
                json.dumps(darkest_night)
            ))
            users_count += 1
            
            for card_id in udata.get("cards", []):
                cur.execute("""
                    INSERT INTO user_inventory (user_id, card_id) VALUES (%s, %s);
                """, (user_id, card_id))
                inventory_count += 1
                
        except Exception as e:
            print(f"⚠️ Ошибка при переносе пользователя {user_id}: {e}")
    
    print(f"✅ Перенесено пользователей: {users_count}")
    print(f"✅ Перенесено карт в инвентарь: {inventory_count}")
    
    # 3. Перенос кланов
    print("\n🔄 Перенос кланов...")
    clans_count = 0
    members_count = 0
    
    for clan_id, cdata in data.get("clans", {}).items():
        try:
            cur.execute("""
                INSERT INTO clans (clan_id, name, leader_id, super_coins, max_members)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (clan_id) DO NOTHING;
            """, (clan_id, cdata["name"], cdata.get("leader_id"), cdata.get("super_coins", 0), cdata.get("max_members", 7)))
            clans_count += 1
            
            for member_id, member_info in cdata.get("members", {}).items():
                cur.execute("""
                    INSERT INTO clan_members (clan_id, user_id, role) VALUES (%s, %s, %s)
                    ON CONFLICT DO NOTHING;
                """, (clan_id, member_id, member_info.get("role", "member")))
                members_count += 1
                
        except Exception as e:
            print(f"⚠️ Ошибка при переносе клана {clan_id}: {e}")
    
    print(f"✅ Перенесено кланов: {clans_count}")
    print(f"✅ Перенесено участников кланов: {members_count}")
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("\n" + "="*50)
    print("✅ МИГРАЦИЯ УСПЕШНО ЗАВЕРШЕНА!")
    print("="*50)
    print(f"📊 Итого:")
    print(f"  • Карт: {cards_count}")
    print(f"  • Пользователей: {users_count}")
    print(f"  • Карт в инвентаре: {inventory_count}")
    print(f"  • Кланов: {clans_count}")
    print(f"  • Участников кланов: {members_count}")
    print("="*50)

if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")
        import traceback
        traceback.print_exc()
