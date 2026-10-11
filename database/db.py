import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = "spendly.db"

def get_db():
    """
    Opens a connection to the SQLite database.
    Sets row_factory to sqlite3.Row for dictionary-like access.
    Enables foreign key constraints.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """
    Initializes the database schema.
    Creates users and expenses tables if they do not exist.
    """
    with get_db() as conn:
        # Create users table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)

        # Create expenses table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        conn.commit()

def seed_db():
    """
    Seeds the database with sample data for development.
    Prevents duplicate inserts by checking if the users table is already populated.
    """
    with get_db() as conn:
        # Check if users already exist
        cursor = conn.execute("SELECT 1 FROM users LIMIT 1")
        if cursor.fetchone():
            return

        # Create a demo user
        demo_password_hash = generate_password_hash("demo123")
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", demo_password_hash)
        )
        user_id = cursor.lastrowid

        # Sample expenses covering all categories
        # Categories: Food, Transport, Bills, Health, Entertainment, Shopping, Other
        expenses = [
            (user_id, 15.50, "Food", "2026-10-01", "Lunch at Cafe"),
            (user_id, 45.00, "Transport", "2026-10-02", "Fuel fill-up"),
            (user_id, 120.00, "Bills", "2026-10-03", "Internet Bill"),
            (user_id, 30.00, "Health", "2026-10-04", "Pharmacy"),
            (user_id, 25.00, "Entertainment", "2026-10-05", "Movie Ticket"),
            (user_id, 60.00, "Shopping", "2026-10-06", "New Shirt"),
            (user_id, 10.00, "Other", "2026-10-07", "Parking fee"),
            (user_id, 12.00, "Food", "2026-10-08", "Coffee and Snack"),
        ]

        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            expenses
        )
        conn.commit()
