"""Authentication logic for the Online Quiz System.

Handles password hashing and the register/login flow. Passwords are never
stored in plain text: we use PBKDF2-HMAC-SHA256 with a random per-user salt
(from Python's standard library, so no extra packages are needed).

A stored password looks like:  "<salt_hex>$<hash_hex>"
"""

import hashlib
import hmac
import os
import sqlite3

import database

# PBKDF2 settings.
_ALGORITHM = "sha256"
_ITERATIONS = 100_000
_SALT_BYTES = 16


def hash_password(password):
    """Return a salted PBKDF2 hash of the password as 'salt$hash' (hex)."""
    salt = os.urandom(_SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(
        _ALGORITHM, password.encode("utf-8"), salt, _ITERATIONS
    )
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password, stored):
    """Return True if `password` matches the stored 'salt$hash' value."""
    try:
        salt_hex, hash_hex = stored.split("$", 1)
        salt = bytes.fromhex(salt_hex)
    except (ValueError, AttributeError):
        return False
    digest = hashlib.pbkdf2_hmac(
        _ALGORITHM, password.encode("utf-8"), salt, _ITERATIONS
    )
    # Constant-time comparison to avoid timing attacks.
    return hmac.compare_digest(digest.hex(), hash_hex)


def register(username, password):
    """Register a new normal user.

    Returns a tuple (user, error_message). On success `user` is a dict and
    `error_message` is None; on failure `user` is None and `error_message`
    explains why.
    """
    username = username.strip()
    if not username:
        return None, "Username cannot be empty."
    if len(password) < 4:
        return None, "Password must be at least 4 characters long."
    if database.username_exists(username):
        return None, "That username is already taken."

    try:
        user_id = database.create_user(username, hash_password(password), "user")
    except sqlite3.IntegrityError:
        # Handles the rare race where the username was taken between checks.
        return None, "That username is already taken."

    return {"id": user_id, "username": username, "role": "user"}, None


def login(username, password):
    """Return the user dict (id, username, role) if credentials are valid.

    Returns None if the user does not exist or the password is wrong.
    """
    user = database.get_user_by_username(username.strip())
    if user is None:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return {"id": user["id"], "username": user["username"], "role": user["role"]}
