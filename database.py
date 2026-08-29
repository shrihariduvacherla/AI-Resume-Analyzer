import sqlite3
import os
import hashlib
import secrets
from datetime import datetime, timedelta

DB_FILE = "data/analysis_history.db"


def init_db():
    """
    Creates the database and the 'history' table if they don't already exist.
    Safe to call every time the app starts — it won't overwrite existing data.
    """
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            final_score REAL,
            skill_match REAL,
            semantic_score REAL,
            matching_skills TEXT,
            missing_skills TEXT
        )
    """)

    connection.commit()
    connection.close()


def save_analysis(final_score, skill_match, semantic_score, matching_skills, missing_skills):
    """
    Saves one analysis result into the database.
    """
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    matching_str = ", ".join(matching_skills)
    missing_str = ", ".join(missing_skills)

    cursor.execute("""
        INSERT INTO history (timestamp, final_score, skill_match, semantic_score, matching_skills, missing_skills)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (timestamp, final_score, skill_match, semantic_score, matching_str, missing_str))

    connection.commit()
    connection.close()


def get_all_analyses():
    """
    Retrieves all saved analyses from the database, most recent first.
    """
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM history ORDER BY id DESC")
    rows = cursor.fetchall()

    connection.close()
    return rows


def init_auth_tables():
    """
    Creates the 'users' and 'login_history' tables if they don't already exist.
    """
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            login_time TEXT
        )
    """)

    connection.commit()
    connection.close()


def hash_password(password, salt=None):
    """
    Hashes a password with a random salt using SHA-256.
    """
    if salt is None:
        salt = secrets.token_hex(16)

    salted_password = (password + salt).encode("utf-8")
    password_hash = hashlib.sha256(salted_password).hexdigest()

    return password_hash, salt


def create_user(username, password):
    """
    Creates a new user account. Returns True if successful,
    False if the username is already taken.
    """
    password_hash, salt = hash_password(password)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (username, password_hash, salt, created_at)
            VALUES (?, ?, ?, ?)
        """, (username, password_hash, salt, timestamp))
        connection.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False

    connection.close()
    return success


def verify_user(username, password):
    """
    Checks whether a username/password combination is correct.
    """
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("SELECT password_hash, salt FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    connection.close()

    if row is None:
        return False

    stored_hash, salt = row
    attempted_hash, _ = hash_password(password, salt)

    return attempted_hash == stored_hash


def log_login(username):
    """
    Records a login event with a timestamp.
    """
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO login_history (username, login_time) VALUES (?, ?)", (username, timestamp))

    connection.commit()
    connection.close()


def get_login_history():
    """
    Retrieves all login events, most recent first.
    """
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("SELECT username, login_time FROM login_history ORDER BY id DESC")
    rows = cursor.fetchall()

    connection.close()
    return rows


def save_remember_token(username, token):
    """
    Saves a 'remember me' token linked to a username, with an expiration date.
    """
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS remember_tokens (
            token TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            expires_at TEXT NOT NULL
        )
    """)

    expires_at = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT OR REPLACE INTO remember_tokens (token, username, expires_at) VALUES (?, ?, ?)",
                   (token, username, expires_at))

    connection.commit()
    connection.close()


def get_username_from_token(token):
    """
    Looks up a 'remember me' token and returns the associated username
    if the token exists and hasn't expired. Returns None otherwise.
    """
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS remember_tokens (
            token TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            expires_at TEXT NOT NULL
        )
    """)

    cursor.execute("SELECT username, expires_at FROM remember_tokens WHERE token = ?", (token,))
    row = cursor.fetchone()
    connection.close()

    if row is None:
        return None

    username, expires_at = row
    expires_at_dt = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")

    if datetime.now() > expires_at_dt:
        return None

    return username


def delete_remember_token(token):
    """
    Deletes a specific 'remember me' token (used on logout).
    """
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM remember_tokens WHERE token = ?", (token,))
    connection.commit()
    connection.close()