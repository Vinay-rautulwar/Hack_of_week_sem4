import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "health_coach.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS health_coach (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        sleep_hours REAL,
        workout_minutes INTEGER,
        workout_intensity INTEGER,
        stress_level INTEGER,
        goal TEXT
    )
    """)

    conn.commit()
    conn.close()

def insert_health_data(data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO health_coach
    (date, sleep_hours, workout_minutes, workout_intensity, stress_level, goal)
    VALUES (date('now'), ?, ?, ?, ?, ?)
    """, (
        data["sleep_hours"],
        data["workout_minutes"],
        data["workout_intensity"],
        data["stress_level"],
        data["goal"]
    ))

    conn.commit()
    conn.close()
