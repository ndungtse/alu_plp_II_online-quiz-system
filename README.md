# Online Quiz System

A menu-driven, command-line quiz application written in Python, using a **SQLite**
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
| `main.py` | Entry point: the auth screen, role-based menus, and input validation. |
| `auth.py` | Password hashing (PBKDF2) and the register/login logic. |
| `quiz.py` | Runs a single quiz (asks questions, keeps score). |
| `database.py` | All SQLite connection and query logic. |
| `config.py` | Reads DB settings from environment / `.env`. |
| `schema.sql` | The database schema (also created automatically on first run). |
| `.env.example` | Template for your local database settings. |

## Accounts and roles

The app requires you to log in or register first. There are two roles:

- **User** – register a new account, then take quizzes, view your own quiz
  history, and see the leaderboard.
- **Admin** – manage the question bank: add, view, update, and delete questions,
  and view all users' scores.

A default admin account is created automatically on first run:

- **Username:** `admin`
- **Password:** `admin123`

Change this password (or the seeded values in `main.py`) before real use.
Passwords are stored only as salted PBKDF2 hashes, never in plain text.

## Requirements

- Python 3.8+

No external packages are required; the app uses Python's built-in `sqlite3` module.

## Setup

### 1. Create and activate a virtual environment (recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

### 2. Configure the database path (optional)

```bash
cp .env.example .env
```

By default the app creates `quiz.db` in the project folder. Change `DB_PATH` in
`.env` if you want the file somewhere else.

### 3. Run the app

```bash
python main.py
```

The database file, tables, starter questions, and the default admin account are
created automatically on first run. Log in as `admin` / `admin123`, or register
your own user account.

## Notes

- On first run the app creates the `questions` and `scores` tables and inserts a
  set of starter questions if the table is empty.
- The database path is read from environment variables (or the `.env` file);
  the `.env` file is git-ignored so local overrides are not committed.
