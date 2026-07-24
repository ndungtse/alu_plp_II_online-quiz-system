"""Configuration for the Online Quiz System.

Reads database settings from environment variables. If a `.env` file exists
next to this file, its values are loaded first (without needing any extra
library). Environment variables already set in the shell take priority over
the `.env` file.
"""

import os

# Path to an optional .env file in the same directory as this script.
_ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")


def _load_env_file(path):
    """Load simple KEY=VALUE lines from a .env file into os.environ.

    Lines that are blank or start with '#' are ignored. Existing environment
    variables are NOT overwritten, so the shell always wins.
    """
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


_load_env_file(_ENV_PATH)


# Database connection settings (with sensible local defaults).
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "127.0.0.1"),
    "port": int(os.environ.get("DB_PORT", "3306")),
    "user": os.environ.get("DB_USER", "quiz_user"),
    "password": os.environ.get("DB_PASSWORD", "quiz_pass"),
    "database": os.environ.get("DB_NAME", "quiz_db"),
}

# Name of the database (kept separate so we can create it before connecting to it).
DB_NAME = DB_CONFIG["database"]
