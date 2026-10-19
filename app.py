from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from database.db import init_db, seed_db, get_db
from database.queries import get_category_breakdown, get_summary_stats, get_recent_transactions, get_user_by_id

app = Flask(__name__)
app.secret_key = "spendly-secret-key-for-dev"

with app.app_context():
    init_db()
    seed_db()



# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register")
def register():
    if session.get("user_id"):
        return redirect(url_for("profile"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("profile"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        with get_db() as db:
            user = db.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,)
            ).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            return redirect(url_for("profile"))

        return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    with get_db() as db:
        user_record = db.execute(
            "SELECT * FROM users WHERE id = ?",
            (session["user_id"],)
        ).fetchone()

    if not user_record:
        return redirect(url_for("login"))

    # Mock User Data using real record
    user_record_full = get_user_by_id(session["user_id"])

    from datetime import datetime
    member_since = "—"
    if user_record_full and user_record_full.get("created_at"):
        try:
            dt = datetime.fromisoformat(user_record_full["created_at"])
            member_since = dt.strftime("%B %Y")
        except ValueError:
            pass

    user = {
        "name": user_record_full["name"] if user_record_full else "User",
        "email": user_record_full["email"] if user_record_full else "N/A",
        "member_since": member_since,
        "initials": "".join([n[0].upper() for n in (user_record_full["name"] if user_record_full else "User").split()])
    }

    # Summary Statistics
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    # Basic date validation
    if start_date and len(start_date) != 10:
        start_date = None
    if end_date and len(end_date) != 10:
        end_date = None

    user_stats = get_summary_stats(session["user_id"], start_date, end_date)
    stats = [
        {"label": "Total Spent", "value": f"₹{user_stats['total_spent']:,.2f}", "icon": "wallet", "delta": ""},
        {"label": "Transactions", "value": str(user_stats["transaction_count"]), "icon": "list", "delta": ""},
        {"label": "Top Category", "value": user_stats["top_category"], "icon": "utensils", "delta": ""}
    ]

    # Recent Transactions
    db_transactions = get_recent_transactions(session["user_id"], start_date, end_date)
    transactions = [
        {
            "date": row["date"],
            "desc": row["description"],
            "cat": row["category"],
            "amount": f"₹{row['amount']:,.2f}",
            "cat_class": f"badge-{row['category'].lower()}"
        }
        for row in db_transactions
    ]

    # Category Breakdown
    category_data = get_category_breakdown(session["user_id"], start_date, end_date)
    colors = ["var(--accent)", "var(--accent-2)", "#6366F1", "#10B981", "#F59E0B", "#EF4444"]

    categories = []
    for i, item in enumerate(category_data):
        categories.append({
            "name": item["name"],
            "amount": f"₹{item['amount']:,.2f}",
            "percent": item["pct"],
            "color": colors[i % len(colors)]
        })

    return render_template("profile.html", user=user, stats=stats, transactions=transactions, categories=categories, start_date=start_date, end_date=end_date)


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
