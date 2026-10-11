import sqlite3
import random
from datetime import datetime, timedelta
from database.db import get_db

def seed_expenses(user_id, count, months):
    categories = {
        "Food": {"range": (50, 800), "weight": 30, "desc": ["Dinner at Swiggy", "Lunch at Office", "Grocery from Blinkit", "Street food", "Cafe Coffee"]},
        "Transport": {"range": (20, 500), "weight": 20, "desc": ["Ola/Uber ride", "Petrol", "Auto rickshaw", "Metro recharge", "Bus fare"]},
        "Bills": {"range": (200, 3000), "weight": 15, "desc": ["Electricity bill", "Water bill", "Wifi bill", "Phone recharge", "Gas cylinder"]},
        "Health": {"range": (100, 2000), "weight": 5, "desc": ["Pharmacy", "Clinic visit", "Medicine", "Dental checkup", "Vitamin supplements"]},
        "Entertainment": {"range": (100, 1500), "weight": 5, "desc": ["Movie ticket", "Netflix subscription", "Gaming zone", "Bowling", "Concert ticket"]},
        "Shopping": {"range": (200, 5000), "weight": 15, "desc": ["Amazon order", "Myntra clothes", "Footwear", "Electronics", "Gift for friend"]},
        "Other": {"range": (50, 1000), "weight": 10, "desc": ["Laundry", "Stationery", "Tips", "Charity", "Miscellaneous"]}
    }

    cat_list = list(categories.keys())
    weights = [categories[c]["weight"] for c in cat_list]

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)

    expenses_to_insert = []
    for _ in range(count):
        category = random.choices(cat_list, weights=weights)[0]
        amount = round(random.uniform(*categories[category]["range"]), 2)
        description = random.choice(categories[category]["desc"])

        # Random date between start_date and end_date
        random_days = random.randint(0, months * 30)
        date_obj = start_date + timedelta(days=random_days)
        date_str = date_obj.strftime("%Y-%m-%d")

        expenses_to_insert.append((user_id, amount, category, date_str, description))

    try:
        conn = get_db()
        with conn:
            cursor = conn.executemany(
                "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                expenses_to_insert
            )

        # Collect data for confirmation
        inserted_count = len(expenses_to_insert)
        dates = [e[3] for e in expenses_to_insert]
        date_range = f"{min(dates)} to {max(dates)}"

        # Sample 5 records
        sample_size = min(5, inserted_count)
        sample = random.sample(expenses_to_insert, sample_size)

        print(f"Successfully inserted {inserted_count} expenses.")
        print(f"Date range: {date_range}")
        print("\nSample records:")
        for s in sample:
            print(f"Date: {s[3]} | Category: {s[2]} | Amount: Rs {s[1]} | Desc: {s[4]}")

    except Exception as e:
        print(f"Error inserting expenses: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    seed_expenses(2, 5, 3)
