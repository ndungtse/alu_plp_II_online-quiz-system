-- Online Quiz System - database schema
-- The application creates this automatically on first run, but you can also
-- run this file manually with:  mysql -u root -p < schema.sql

CREATE DATABASE IF NOT EXISTS quiz_db
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE quiz_db;

CREATE TABLE IF NOT EXISTS questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    level ENUM('easy','medium','hard') NOT NULL DEFAULT 'easy',
    question_text VARCHAR(500) NOT NULL,
    option_a VARCHAR(255) NOT NULL,
    option_b VARCHAR(255) NOT NULL,
    option_c VARCHAR(255) NOT NULL,
    option_d VARCHAR(255) NOT NULL,
    correct_option CHAR(1) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    player_name VARCHAR(100) NOT NULL,
    level VARCHAR(10) NOT NULL,
    score INT NOT NULL,
    total INT NOT NULL,
    taken_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
