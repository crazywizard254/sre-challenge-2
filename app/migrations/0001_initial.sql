-- Initial migration: create parts table for the classifieds application
-- This file is applied by the seed job if present.

CREATE TABLE IF NOT EXISTS parts (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    price INTEGER,
    location TEXT,
    image_url TEXT,
    contact_email TEXT,
    contact_phone TEXT,
    validation_token VARCHAR(128),
    is_validated TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
