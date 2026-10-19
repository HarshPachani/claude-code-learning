import pytest
from app import app as flask_app
from database.db import init_db, get_db
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    flask_app.config.update({
        'TESTING': True,
        'DATABASE': ':memory:',  # isolated in-memory DB per test
        'SECRET_KEY': 'test-secret',
        'WTF_CSRF_ENABLED': False,
    })

    # Override get_db to use the in-memory database for the test session
    import database.db as db_module

    # Create a persistent connection for the duration of the test
    conn = db_module.sqlite3.connect(':memory:')
    conn.row_factory = db_module.sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    def mock_get_db():
        return conn

    db_module.get_db = mock_get_db

    with flask_app.app_context():
        init_db()
        yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client, app):
    """A test client that is already logged in."""
    # We must ensure the user exists in the DB before logging in
    with app.app_context():
        with get_db() as db:
            db.execute(
                "INSERT OR IGNORE INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                ("Test User", "test@example.com", generate_password_hash("testpass"))
            )
            db.commit()

    client.post('/login', data={'email': 'test@example.com', 'password': 'testpass'})
    return client

@pytest.fixture
def seed_expenses(app):
    """Inserts a set of controlled expenses for date filtering tests."""
    with app.app_context():
        with get_db() as db:
            # Get the user ID for the user created in auth_client
            user = db.execute("SELECT id FROM users WHERE email = ?", ("test@example.com",)).fetchone()
            if not user:
                pytest.fail("User must be created before seeding expenses")

            user_id = user["id"]
            expenses = [
                (user_id, 100.0, "Food", "2023-01-01", "Expense 1"),
                (user_id, 200.0, "Transport", "2023-01-15", "Expense 2"),
                (user_id, 300.0, "Bills", "2023-02-01", "Expense 3"),
                (user_id, 400.0, "Food", "2023-02-15", "Expense 4"),
                (user_id, 500.0, "Health", "2023-03-01", "Expense 5"),
            ]
            db.executemany(
                "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                expenses
            )
            db.commit()

class TestDateFilterProfile:

    def test_profile_no_filters_loads_all(self, auth_client, seed_expenses):
        """Happy Path: Profile page loads with no filters and shows all transactions."""
        response = auth_client.get('/profile')
        assert response.status_code == 200
        # Total spent: 100+200+300+400+500 = 1500
        assert b"1,500.00" in response.data
        # Transaction count: 5
        assert b"5" in response.data
        # All 5 descriptions should be present
        for i in range(1, 6):
            assert f"Expense {i}".encode() in response.data

    def test_profile_start_date_filter(self, auth_client, seed_expenses):
        """Start Date Filter: Returns transactions on or after start_date."""
        # Filter from 2023-02-01 onwards (should see Expense 3, 4, 5)
        response = auth_client.get('/profile?start_date=2023-02-01')
        assert response.status_code == 200
        assert b"1,200.00" in response.data # 300+400+500
        assert b"3" in response.data
        assert b"Expense 3" in response.data
        assert b"Expense 4" in response.data
        assert b"Expense 5" in response.data
        assert b"Expense 1" not in response.data
        assert b"Expense 2" not in response.data

    def test_profile_end_date_filter(self, auth_client, seed_expenses):
        """End Date Filter: Returns transactions on or before end_date."""
        # Filter up to 2023-01-15 (should see Expense 1, 2)
        response = auth_client.get('/profile?end_date=2023-01-15')
        assert response.status_code == 200
        assert b"300.00" in response.data # 100+200
        assert b"2" in response.data
        assert b"Expense 1" in response.data
        assert b"Expense 2" in response.data
        assert b"Expense 3" not in response.data

    def test_profile_date_range_filter(self, auth_client, seed_expenses):
        """Date Range: Returns transactions strictly within the window."""
        # Filter between 2023-01-10 and 2023-02-20 (should see Expense 2, 3, 4)
        response = auth_client.get('/profile?start_date=2023-01-10&end_date=2023-02-20')
        assert response.status_code == 200
        assert b"900.00" in response.data # 200+300+400
        assert b"3" in response.data
        assert b"Expense 2" in response.data
        assert b"Expense 3" in response.data
        assert b"Expense 4" in response.data
        assert b"Expense 1" not in response.data
        assert b"Expense 5" not in response.data

    def test_profile_empty_range(self, auth_client, seed_expenses):
        """Empty Range: A range with no transactions returns zero stats and empty list."""
        response = auth_client.get('/profile?start_date=2024-01-01&end_date=2024-01-31')
        assert response.status_code == 200
        assert b"0.00" in response.data
        assert b"0" in response.data
        assert b"Expense 1" not in response.data
        # Top category should be the placeholder "—"
        assert "—" in response.data.decode('utf-8', errors='ignore')

    def test_profile_auth_guard(self, client):
        """Auth Guard: Unauthenticated access to profile redirects to login."""
        response = client.get('/profile')
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_profile_ui_persistence(self, auth_client, seed_expenses):
        """UI Persistence: Verify that start_date and end_date are passed back to the template."""
        start = "2023-01-01"
        end = "2023-01-31"
        response = auth_client.get(f'/profile?start_date={start}&end_date={end}')
        assert response.status_code == 200
        # Assuming the inputs in profile.html use the value attribute to persist data
        assert f'value="{start}"'.encode() in response.data
        assert f'value="{end}"'.encode() in response.data
