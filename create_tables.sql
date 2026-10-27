-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(50) PRIMARY KEY,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    cents BIGINT DEFAULT 0,
    free_rolls INT DEFAULT 0,
    casino_attempts INT DEFAULT 5,
    last_casino_reset BIGINT DEFAULT 0,
    batpass_active_until TIMESTAMP,
    avatar_url TEXT,
    quests_data JSONB DEFAULT '{}',
    darkest_night JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица карт (справочник)
CREATE TABLE IF NOT EXISTS cards (
    card_id INT PRIMARY KEY,
    title VARCHAR(255),
    rarity VARCHAR(50),
    image_url TEXT,
    file_id TEXT,
    media_type VARCHAR(50),
    available BOOLEAN DEFAULT TRUE
);

-- Инвентарь пользователей
CREATE TABLE IF NOT EXISTS user_inventory (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
    card_id INT REFERENCES cards(card_id) ON DELETE CASCADE
);

-- Кланы
CREATE TABLE IF NOT EXISTS clans (
    clan_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255),
    leader_id VARCHAR(50) REFERENCES users(user_id),
    super_coins INT DEFAULT 0,
    max_members INT DEFAULT 7,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Участники кланов
CREATE TABLE IF NOT EXISTS clan_members (
    clan_id VARCHAR(50) REFERENCES clans(clan_id) ON DELETE CASCADE,
    user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (clan_id, user_id)
);

-- Индексы для ускорения поиска
CREATE INDEX IF NOT EXISTS idx_user_inventory_user_id ON user_inventory(user_id);
CREATE INDEX IF NOT EXISTS idx_user_inventory_card_id ON user_inventory(card_id);
CREATE INDEX IF NOT EXISTS idx_clan_members_clan_id ON clan_members(clan_id);
CREATE INDEX IF NOT EXISTS idx_clan_members_user_id ON clan_members(user_id);
