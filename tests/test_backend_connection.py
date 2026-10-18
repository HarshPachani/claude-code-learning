import pytest
from app import app as flask_app
from database.db import init_db, seed_db
from database.queries import (
    get_user_by_id,
    get_summary_stats,
    get_recent_transactions,
    get_category_breakdown
)
import sqlite3
import os

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Ensure we use a test database
    # In a real scenario, we'd override the DB path in app.py
    # For this exercise, we'll use the standard db but seed it
    init_db()
    seed_db()

def test_get_user_by_id():
    # Seed user usually has ID 1
    user = get_user_by_id(1)
    assert user is not None
    assert user["name"] == "Demo User"
    assert user["email"] == "demo@spendly.com"

    # Non-existent user
    assert get_user_by_id(999) is None

def test_get_summary_stats():
    stats = get_summary_stats(1)
    assert stats["total_spent"] == 317.5
    assert stats["transaction_count"] == 8
    assert stats["top_category"] == "Bills"

    # User with no expenses
    # Create a temporary user
    with sqlite3.connect("spendly.db") as conn:
        conn.execute("INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
                     ("Empty User", "empty@test.com", "hash", "2026-01-01"))
        empty_id = conn.execute("SELECT id FROM users WHERE email = 'empty@test.com'").fetchone()[0]

    stats_empty = get_summary_stats(empty_id)
    assert stats_empty["total_spent"] == 0.0
    assert stats_empty["transaction_count"] == 0
    assert stats_empty["top_category"] == "—"

def test_get_recent_transactions():
    txs = get_recent_transactions(1)
    assert len(txs) == 8
    # Check order: should be newest first
    dates = [t["date"] for t in txs]
    assert dates == sorted(dates, reverse=True)

def test_get_category_breakdown():
    breakdown = get_category_breakdown(1)
    # Seed has 7 categories
    assert len(breakdown) == 7

    # Percentages must sum to 100
    total_pct = sum(item["pct"] for item in breakdown)
    assert total_pct == 100

    # Order: highest amount first
    amounts = [item["amount"] for item in breakdown]
    assert amounts == sorted(amounts, reverse=True)

def test_profile_route_auth():
    client = flask_app.test_client()

    # Unauthenticated
    response = client.get("/profile")
    assert response.status_code == 302
    assert "login" in response.location

    # Authenticated
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    response = client.get("/profile")
    assert response.status_code == 200
    assert b"Demo User" in response.data
    assert b"demo@spendly.com" in response.data
    assert b"\xe2\x82\xb9317.50" in response.data
    assert b"Bills" in response.data
    assert b"\xe2\x82\xb9" in response.data
