"""Database access layer for the Online Quiz System.

This module handles the SQLite connection and all the SQL queries used by the
application: creating the schema, seeding starter questions, reading questions
for a quiz, adding questions, and saving/reading scores.
"""

import os
import sqlite3

import config

LEVELS = ("easy", "medium", "hard")


def get_connection():
    """Return a new SQLite connection with rows accessible by column name."""
    db_dir = os.path.dirname(config.DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Create the database file and tables if they do not already exist.

    Returns True on success, False if setup failed.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user'
                    CHECK (role IN ('admin', 'user')),
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL DEFAULT 'easy'
                    CHECK (level IN ('easy', 'medium', 'hard')),
                question_text TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                correct_option TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                player_name TEXT NOT NULL,
                level TEXT NOT NULL,
                score INTEGER NOT NULL,
                total INTEGER NOT NULL,
                taken_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Migration: older databases have a `scores` table without user_id.
        # Add the column if it is missing so existing data keeps working.
        cursor.execute("PRAGMA table_info(scores)")
        score_columns = [row["name"] for row in cursor.fetchall()]
        if "user_id" not in score_columns:
            cursor.execute("ALTER TABLE scores ADD COLUMN user_id INTEGER")

        conn.commit()
        cursor.close()
        conn.close()
        return True
    except sqlite3.Error as exc:
        print(f"\n[Database error] Could not initialise the database: {exc}")
        return False


def seed_questions_if_empty():
    """Insert a set of starter questions the first time the app runs."""
    starter = [
        ("easy", "What is the capital city of Rwanda?",
         "Nairobi", "Kigali", "Kampala", "Dodoma", "B"),
        ("easy", "Which symbol is used for addition in Python?",
         "-", "*", "+", "/", "C"),
        ("easy", "How many days are there in a week?",
         "5", "6", "7", "8", "C"),
        ("easy", "Which planet is known as the Red Planet?",
         "Earth", "Mars", "Jupiter", "Venus", "B"),
        ("easy", "What does 'CPU' stand for?",
         "Central Process Unit", "Central Processing Unit",
         "Computer Personal Unit", "Central Personal Unit", "B"),
        ("medium", "Which data type is used to store True/False in Python?",
         "int", "str", "bool", "float", "C"),
        ("medium", "What is the result of 7 // 2 in Python?",
         "3.5", "3", "4", "2", "B"),
        ("medium", "Which keyword is used to define a function in Python?",
         "func", "define", "def", "function", "C"),
        ("medium", "In which continent is Egypt located?",
         "Asia", "Europe", "Africa", "Australia", "C"),
        ("hard", "What is the time complexity of binary search?",
         "O(n)", "O(log n)", "O(n^2)", "O(1)", "B"),
        ("hard", "Which SQL clause is used to filter grouped rows?",
         "WHERE", "GROUP BY", "HAVING", "ORDER BY", "C"),
        ("hard", "What is the output of len(set([1, 1, 2, 3, 3]))?",
         "5", "4", "3", "2", "C"),
    ]
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM questions")
        (count,) = cursor.fetchone()
        if count == 0:
            cursor.executemany(
                """
                INSERT INTO questions
                    (level, question_text, option_a, option_b,
                     option_c, option_d, correct_option)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                starter,
            )
            conn.commit()
            print(f"Seeded {len(starter)} starter questions.")
        cursor.close()
        conn.close()
    except sqlite3.Error as exc:
        print(f"\n[Database error] Could not seed questions: {exc}")


def get_questions_by_level(level, limit=5):
    """Return up to `limit` random questions for the given difficulty level.

    Each row is returned as a dictionary.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, level, question_text, option_a, option_b,
               option_c, option_d, correct_option
        FROM questions
        WHERE level = ?
        ORDER BY RANDOM()
        LIMIT ?
        """,
        (level, limit),
    )
    rows = [dict(row) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return rows


def count_questions_by_level(level):
    """Return how many questions exist for a level."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM questions WHERE level = ?", (level,))
    (count,) = cursor.fetchone()
    cursor.close()
    conn.close()
    return count


def add_question(level, text, opt_a, opt_b, opt_c, opt_d, correct_option):
    """Insert a new question and return its new id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO questions
            (level, question_text, option_a, option_b,
             option_c, option_d, correct_option)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (level, text, opt_a, opt_b, opt_c, opt_d, correct_option),
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return new_id


def save_score(user_id, player_name, level, score, total):
    """Save a completed quiz attempt for the given user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO scores (user_id, player_name, level, score, total)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, player_name, level, score, total),
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_score_history(limit=20):
    """Return the most recent quiz attempts (all users) as dictionaries."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT player_name, level, score, total, taken_at
        FROM scores
        ORDER BY taken_at DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = [dict(row) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return rows


def get_scores_by_user(user_id, limit=20):
    """Return the most recent quiz attempts for a single user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT player_name, level, score, total, taken_at
        FROM scores
        WHERE user_id = ?
        ORDER BY taken_at DESC
        LIMIT ?
        """,
        (user_id, limit),
    )
    rows = [dict(row) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return rows


# --------------------------------------------------------------------------- #
# User accounts
# --------------------------------------------------------------------------- #
def create_user(username, password_hash, role="user"):
    """Insert a new user and return the new user's id.

    Raises sqlite3.IntegrityError if the username already exists.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO users (username, password_hash, role)
        VALUES (?, ?, ?)
        """,
        (username, password_hash, role),
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return new_id


def get_user_by_username(username):
    """Return a user row as a dictionary, or None if not found."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, password_hash, role FROM users WHERE username = ?",
        (username,),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return dict(row) if row else None


def username_exists(username):
    """Return True if a user with this username already exists."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    found = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return found


def seed_admin_if_missing(username, password_hash):
    """Create a default admin account if no admin user exists yet."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
    (admin_count,) = cursor.fetchone()
    if admin_count == 0:
        cursor.execute(
            """
            INSERT INTO users (username, password_hash, role)
            VALUES (?, ?, 'admin')
            """,
            (username, password_hash),
        )
        conn.commit()
        print(f"Created default admin account: '{username}'.")
    cursor.close()
    conn.close()


# --------------------------------------------------------------------------- #
# Question management (admin CRUD)
# --------------------------------------------------------------------------- #
def get_all_questions(level=None):
    """Return all questions, optionally filtered by level, ordered by id."""
    conn = get_connection()
    cursor = conn.cursor()
    if level:
        cursor.execute(
            """
            SELECT id, level, question_text, option_a, option_b,
                   option_c, option_d, correct_option
            FROM questions
            WHERE level = ?
            ORDER BY id
            """,
            (level,),
        )
    else:
        cursor.execute(
            """
            SELECT id, level, question_text, option_a, option_b,
                   option_c, option_d, correct_option
            FROM questions
            ORDER BY id
            """
        )
    rows = [dict(row) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return rows


def get_question_by_id(question_id):
    """Return a single question as a dictionary, or None if not found."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, level, question_text, option_a, option_b,
               option_c, option_d, correct_option
        FROM questions
        WHERE id = ?
        """,
        (question_id,),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return dict(row) if row else None


def update_question(question_id, level, text, opt_a, opt_b, opt_c, opt_d,
                    correct_option):
    """Update an existing question. Returns the number of rows changed."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE questions
        SET level = ?, question_text = ?, option_a = ?, option_b = ?,
            option_c = ?, option_d = ?, correct_option = ?
        WHERE id = ?
        """,
        (level, text, opt_a, opt_b, opt_c, opt_d, correct_option, question_id),
    )
    conn.commit()
    changed = cursor.rowcount
    cursor.close()
    conn.close()
    return changed


def delete_question(question_id):
    """Delete a question by id. Returns the number of rows deleted."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
    conn.commit()
    deleted = cursor.rowcount
    cursor.close()
    conn.close()
    return deleted
