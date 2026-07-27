"""Configuration for the Online Quiz System.

Reads database settings from environment variables. If a `.env` file exists
next to this file, its values are loaded first (without needing any extra
library). Environment variables already set in the shell take priority over
the `.env` file.
"""

import os

_ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))


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

_DEFAULT_DB_PATH = os.path.join(_BASE_DIR, "quiz.db")
_db_path = os.environ.get("DB_PATH", _DEFAULT_DB_PATH)
DB_PATH = _db_path if os.path.isabs(_db_path) else os.path.join(_BASE_DIR, _db_path)
