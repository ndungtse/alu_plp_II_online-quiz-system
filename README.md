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
| `main.py` | Entry point: the menu loop and input validation. |
| `quiz.py` | Runs a single quiz (asks questions, keeps score). |
| `database.py` | All SQLite connection and query logic. |
| `config.py` | Reads DB settings from environment / `.env`. |
| `schema.sql` | The database schema (also created automatically on first run). |
| `.env.example` | Template for your local database settings. |

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

The database file, tables, and starter questions are created automatically on
first run.

## Notes

- On first run the app creates the `questions` and `scores` tables and inserts a
  set of starter questions if the table is empty.
- The database path is read from environment variables (or the `.env` file);
  the `.env` file is git-ignored so local overrides are not committed.
