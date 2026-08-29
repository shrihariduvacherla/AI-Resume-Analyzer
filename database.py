import sqlite3
from datetime import datetime

DB_FILE = "data/analysis_history.db"


def init_db():
    """
    Creates the database and the 'history' table if they don't already exist.
    Safe to call every time the app starts — it won't overwrite existing data.
    """
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
    matching_skills and missing_skills are lists, so we join them into
    comma-separated strings since SQLite stores plain text, not Python lists.
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