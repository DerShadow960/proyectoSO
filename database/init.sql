-- Tabla de Usuarios
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    pswdhash TEXT NOT NULL,
    balance DECIMAL(12, 2) NOT NULL
    
);

-- Tabla de Partidas 
CREATE TABLE IF NOT EXISTS gamelogs (
    id SERIAL PRIMARY KEY,
    userid INTEGER REFERENCES users(id),
    gametype VARCHAR(20), -- 'blackjack', 'ruleta', 'tragamonedas', 'poker' 
    betamount DECIMAL(12, 2), 
    result VARCHAR(10) -- 'win', 'loss', 'draw'
);

-- Tabla para el Chat Global
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    userid INTEGER REFERENCES users(id),
    message TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);