# Online Quiz System

A menu-driven, command-line quiz application written in Python, using a **MySQL**
database to store quiz questions and player scores. Built for the Peer Learning
Project (Group 26).

## Features

1. **Take a Quiz** – pick a difficulty level (Easy / Medium / Hard) and answer
   multiple-choice questions one at a time, with instant feedback and a final score.
2. **Add a Question (Admin)** – add new questions to the database.
3. **View Score History** – see recent quiz attempts and scores.
4. **Exit**.

## Project structure

| File | Purpose |
| ---- | ------- |
| `main.py` | Entry point: the menu loop and input validation. |
| `quiz.py` | Runs a single quiz (asks questions, keeps score). |
| `database.py` | All MySQL connection and query logic. |
| `config.py` | Reads DB settings from environment / `.env`. |
| `schema.sql` | The database schema (also created automatically on first run). |
| `requirements.txt` | Python dependencies. |
| `.env.example` | Template for your local database settings. |

## Requirements

- Python 3.8+
- A running MySQL (or MariaDB) server
- The `mysql-connector-python` package

## Setup

### 1. Create and activate a virtual environment (recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the database connection

```bash
cp .env.example .env
```

Then edit `.env` with your MySQL host, user, and password.

### 4. Create the database user (one-time, run in MySQL as an admin)

```sql
CREATE DATABASE IF NOT EXISTS quiz_db;
CREATE USER IF NOT EXISTS 'quiz_user'@'localhost' IDENTIFIED BY 'quiz_pass';
GRANT ALL PRIVILEGES ON quiz_db.* TO 'quiz_user'@'localhost';
FLUSH PRIVILEGES;
```

> The application will create the tables and seed starter questions automatically
> the first time it runs, so you do **not** need to run `schema.sql` by hand.

### 5. Run the app

```bash
python main.py
```

## Notes

- On first run the app creates the `questions` and `scores` tables and inserts a
  set of starter questions if the table is empty.
- Database credentials are read from environment variables (or the `.env` file);
  the `.env` file is git-ignored so secrets are not committed.
