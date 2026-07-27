"""Database access layer for the Online Quiz System.

This module handles the MySQL connection and all the SQL queries used by the
application: creating the schema, seeding starter questions, reading questions
for a quiz, adding questions, and saving/reading scores.

We use the official `mysql-connector-python` driver.
"""

import mysql.connector
from mysql.connector import Error

import config

# The three difficulty levels the quiz supports.
LEVELS = ("easy", "medium", "hard")


def get_connection(include_database=True):
    """Return a new MySQL connection.

    When include_database is False we connect to the server without selecting a
    database. That is needed the very first time, so we can create the database
    if it does not exist yet.
    """
    settings = {
        "host": config.DB_CONFIG["host"],
        "port": config.DB_CONFIG["port"],
        "user": config.DB_CONFIG["user"],
        "password": config.DB_CONFIG["password"],
    }
    if include_database:
        settings["database"] = config.DB_CONFIG["database"]
    return mysql.connector.connect(**settings)


def init_database():
    """Create the database and tables if they do not already exist.

    Returns True on success, False if the connection failed.
    """
    try:
        # Step 1: connect without a database and create it if needed.
        conn = get_connection(include_database=False)
        cursor = conn.cursor()
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {config.DB_NAME} "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        conn.commit()
        cursor.close()
        conn.close()

        # Step 2: connect to the database and create the tables.
        conn = get_connection(include_database=True)
        cursor = conn.cursor()

        cursor.execute(
            """
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
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS scores (
                id INT AUTO_INCREMENT PRIMARY KEY,
                player_name VARCHAR(100) NOT NULL,
                level VARCHAR(10) NOT NULL,
                score INT NOT NULL,
                total INT NOT NULL,
                taken_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as exc:
        print(f"\n[Database error] Could not initialise the database: {exc}")
        return False


def seed_questions_if_empty():
    """Insert a set of starter questions the first time the app runs."""
    starter = [
        # (level, question, A, B, C, D, correct)
        (
            "easy",
            "What is the capital city of Rwanda?",
            "Nairobi",
            "Kigali",
            "Kampala",
            "Dodoma",
            "B",
        ),
        (
            "easy",
            "Which symbol is used for addition in Python?",
            "-",
            "*",
            "+",
            "/",
            "C",
        ),
        ("easy", "How many days are there in a week?", "5", "6", "7", "8", "C"),
        (
            "easy",
            "Which planet is known as the Red Planet?",
            "Earth",
            "Mars",
            "Jupiter",
            "Venus",
            "B",
        ),
        (
            "easy",
            "What does 'CPU' stand for?",
            "Central Process Unit",
            "Central Processing Unit",
            "Computer Personal Unit",
            "Central Personal Unit",
            "B",
        ),
        (
            "medium",
            "Which data type is used to store True/False in Python?",
            "int",
            "str",
            "bool",
            "float",
            "C",
        ),
        (
            "medium",
            "What is the result of 7 // 2 in Python?",
            "3.5",
            "3",
            "4",
            "2",
            "B",
        ),
        (
            "medium",
            "Which keyword is used to define a function in Python?",
            "func",
            "define",
            "def",
            "function",
            "C",
        ),
        (
            "medium",
            "In which continent is Egypt located?",
            "Asia",
            "Europe",
            "Africa",
            "Australia",
            "C",
        ),
        (
            "hard",
            "What is the time complexity of binary search?",
            "O(n)",
            "O(log n)",
            "O(n^2)",
            "O(1)",
            "B",
        ),
        (
            "hard",
            "Which SQL clause is used to filter grouped rows?",
            "WHERE",
            "GROUP BY",
            "HAVING",
            "ORDER BY",
            "C",
        ),
        (
            "hard",
            "What is the output of len(set([1, 1, 2, 3, 3]))?",
            "5",
            "4",
            "3",
            "2",
            "C",
        ),
    ]
    try:
        conn = get_connection(include_database=True)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM questions")
        (count,) = cursor.fetchone()
        if count == 0:
            cursor.executemany(
                """
                INSERT INTO questions
                    (level, question_text, option_a, option_b,
                     option_c, option_d, correct_option)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                starter,
            )
            conn.commit()
            print(f"Seeded {cursor.rowcount} starter questions.")
        cursor.close()
        conn.close()
    except Error as exc:
        print(f"\n[Database error] Could not seed questions: {exc}")


def get_questions_by_level(level, limit=5):
    """Return up to `limit` random questions for the given difficulty level.

    Each row is returned as a dictionary.
    """
    conn = get_connection(include_database=True)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, level, question_text, option_a, option_b,
               option_c, option_d, correct_option
        FROM questions
        WHERE level = %s
        ORDER BY RAND()
        LIMIT %s
        """,
        (level, limit),
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def count_questions_by_level(level):
    """Return how many questions exist for a level."""
    conn = get_connection(include_database=True)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM questions WHERE level = %s", (level,))
    (count,) = cursor.fetchone()
    cursor.close()
    conn.close()
    return count


def add_question(level, text, opt_a, opt_b, opt_c, opt_d, correct_option):
    """Insert a new question and return its new id."""
    conn = get_connection(include_database=True)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO questions
            (level, question_text, option_a, option_b,
             option_c, option_d, correct_option)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (level, text, opt_a, opt_b, opt_c, opt_d, correct_option),
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return new_id


def save_score(player_name, level, score, total):
    """Save a completed quiz attempt."""
    conn = get_connection(include_database=True)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO scores (player_name, level, score, total)
        VALUES (%s, %s, %s, %s)
        """,
        (player_name, level, score, total),
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_score_history(limit=20):
    """Return the most recent quiz attempts as a list of dictionaries."""
    conn = get_connection(include_database=True)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT player_name, level, score, total, taken_at
        FROM scores
        ORDER BY taken_at DESC
        LIMIT %s
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
