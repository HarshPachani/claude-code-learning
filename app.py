from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from database.db import init_db, seed_db, get_db

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
    user = {
        "name": user_record["name"],
        "email": user_record["email"],
        "member_since": "October 2023",
        "initials": "".join([n[0].upper() for n in user_record["name"].split()])
    }

    # Summary Statistics
    stats = [
        {"label": "Total Spent", "value": "₹45,200", "icon": "wallet", "delta": "+2.5% vs last month"},
        {"label": "Transactions", "value": "128", "icon": "list", "delta": "12 this week"},
        {"label": "Top Category", "value": "Dining", "icon": "utensils", "delta": "34% of total"}
    ]

    # Recent Transactions
    transactions = [
        {"date": "2023-10-10", "desc": "Starbucks Coffee", "cat": "Dining", "amount": "-₹350", "cat_class": "badge-dining"},
        {"date": "2023-10-09", "desc": "Uber Ride", "cat": "Transport", "amount": "-₹1,200", "cat_class": "badge-transport"},
        {"date": "2023-10-08", "desc": "Amazon Shopping", "cat": "Shopping", "amount": "-₹4,500", "cat_class": "badge-shopping"},
        {"date": "2023-10-07", "desc": "Monthly Rent", "cat": "Housing", "amount": "-₹15,000", "cat_class": "badge-housing"},
        {"date": "2023-10-06", "desc": "Freelance Payment", "cat": "Income", "amount": "+₹20,000", "cat_class": "badge-income"},
    ]

    # Category Breakdown
    categories = [
        {"name": "Housing", "amount": "₹15,000", "percent": 33, "color": "var(--accent)"},
        {"name": "Shopping", "amount": "₹8,000", "percent": 18, "color": "var(--accent-2)"},
        {"name": "Dining", "amount": "₹6,500", "percent": 14, "color": "#6366F1"},
        {"name": "Transport", "amount": "₹4,000", "percent": 9, "color": "#10B981"},
    ]

    return render_template("profile.html", user=user, stats=stats, transactions=transactions, categories=categories)


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
