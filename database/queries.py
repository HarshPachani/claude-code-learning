from database.db import get_db

def _apply_date_filter(user_id, start_date, end_date):
    query = "WHERE user_id = ?"
    params = [user_id]
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
    return query, params

def get_user_by_id(user_id):
    with get_db() as db:
        row = db.execute(
            "SELECT name, email, created_at FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        return dict(row) if row else None

def get_recent_transactions(user_id, start_date=None, end_date=None, limit=10):
    where_clause, params = _apply_date_filter(user_id, start_date, end_date)
    with get_db() as db:
        query = f"SELECT date, description, category, amount FROM expenses {where_clause} ORDER BY date DESC LIMIT ?"
        params.append(limit)
        rows = db.execute(query, params).fetchall()
        return [dict(row) for row in rows]

def get_summary_stats(user_id, start_date=None, end_date=None):
    with get_db() as db:
        # Total Spent and Transaction Count
        where_clause, params = _apply_date_filter(user_id, start_date, end_date)
        totals = db.execute(
            f"SELECT SUM(amount) as total_spent, COUNT(*) as transaction_count FROM expenses {where_clause}",
            params
        ).fetchone()

        # Top Category
        # Reuse the where_clause and params since inputs are identical
        top_cat_row = db.execute(
            f"SELECT category FROM expenses {where_clause} GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1",
            params
        ).fetchone()

        total_spent = totals["total_spent"] if totals and totals["total_spent"] is not None else 0.0
        transaction_count = totals["transaction_count"] if totals else 0
        top_category = top_cat_row["category"] if top_cat_row else "—"

        return {
            "total_spent": float(total_spent),
            "transaction_count": int(transaction_count),
            "top_category": top_category
        }

def get_category_breakdown(user_id, start_date=None, end_date=None):
    with get_db() as db:
        where_clause, params = _apply_date_filter(user_id, start_date, end_date)
        rows = db.execute(
            f"SELECT category, SUM(amount) as total FROM expenses {where_clause} GROUP BY category ORDER BY total DESC",
            params
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
