from database.db import get_db

def get_user_by_id(user_id):
    with get_db() as db:
        row = db.execute(
            "SELECT name, email, created_at FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        return dict(row) if row else None

def get_recent_transactions(user_id, limit=10):
    with get_db() as db:
        rows = db.execute(
            "SELECT date, description, category, amount FROM expenses WHERE user_id = ? ORDER BY date DESC LIMIT ?",
            (user_id, limit)
        ).fetchall()
        return [dict(row) for row in rows]

def get_summary_stats(user_id):
    with get_db() as db:
        # Total Spent and Transaction Count
        totals = db.execute(
            "SELECT SUM(amount) as total_spent, COUNT(*) as transaction_count FROM expenses WHERE user_id = ?",
            (user_id,)
        ).fetchone()

        # Top Category
        top_cat_row = db.execute(
            "SELECT category FROM expenses WHERE user_id = ? GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1",
            (user_id,)
        ).fetchone()

        total_spent = totals["total_spent"] if totals and totals["total_spent"] is not None else 0.0
        transaction_count = totals["transaction_count"] if totals else 0
        top_category = top_cat_row["category"] if top_cat_row else "—"

        return {
            "total_spent": float(total_spent),
            "transaction_count": int(transaction_count),
            "top_category": top_category
        }

def get_category_breakdown(user_id):
    with get_db() as db:
        rows = db.execute(
            "SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ? GROUP BY category ORDER BY total DESC",
            (user_id,)
        ).fetchall()

        if not rows:
            return []

        data = [dict(row) for row in rows]
        grand_total = sum(item['total'] for item in data)

        if grand_total == 0:
            return [{"name": item['category'], "amount": item['total'], "pct": 0} for item in data]

        results = []
        total_pct = 0

        for i, item in enumerate(data):
            pct = round((item['total'] / grand_total) * 100)
            results.append({
                "name": item['category'],
                "amount": item['total'],
                "pct": pct
            })
            total_pct += pct

        # Adjust the largest category to ensure sum is exactly 100
        diff = 100 - total_pct
        if diff != 0:
            results[0]['pct'] += diff

        return results
