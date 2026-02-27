-- Tabla de Usuarios (Ciberseguridad: Aquí guardaremos el HASH, no la pswd plana)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    balance DECIMAL(12, 2) DEFAULT 1000.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Partidas (Para el historial y auditoría)
CREATE TABLE IF NOT EXISTS game_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    game_type VARCHAR(20), -- 'blackjack', 'ruleta', etc.
    bet_amount DECIMAL(12, 2),
    result VARCHAR(10), -- 'win', 'loss', 'draw'
    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para el Chat Global
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    message TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);