import csv
from io import StringIO
import urllib.parse

from flask import Flask, Response, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash

from dotenv import load_dotenv

load_dotenv()

from api.traffic import analyze_domain
from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USERNAME
from models import SearchHistory, User, db

import os


app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "dev-secret-key-change-in-production"
)

database_url = os.getenv("DATABASE_URL")

if database_url:
    database_url = database_url.replace(
        "postgres://",
        "postgresql://",
        1
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url

else:
    encoded_password = urllib.parse.quote_plus(DB_PASSWORD)

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql://{DB_USERNAME}:{encoded_password}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )


app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"



@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def get_dashboard_context(result=None):
    history = (
        SearchHistory.query.filter_by(user_id=current_user.id)
        .order_by(SearchHistory.id.desc())
        .all()
    )

    top_domain = (
        db.session.query(
            SearchHistory.url,
            func.count(SearchHistory.url).label("search_count"),
        )
        .filter_by(user_id=current_user.id)
        .group_by(SearchHistory.url)
        .order_by(func.count(SearchHistory.url).desc())
        .first()
    )

    return {
        "history": history,
        "result": result,
        "total_searches": len(history),
        "top_domain": top_domain,
    }


with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables initialized.")
    except Exception as exc:
        print(f"❌ Failed to connect to database: {exc}")


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("Please fill in all fields.", "danger")
            return render_template("register.html")

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing_user:
            flash("That username or email is already registered.", "warning")
            return render_template("register.html")

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
        )

        try:
            db.session.add(user)
            db.session.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))
        except Exception:
            db.session.rollback()
            flash("Registration failed. Please try again.", "danger")
            return render_template("register.html")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "danger")
        return render_template("login.html")

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", **get_dashboard_context())


@app.route("/analyze", methods=["POST"])
@login_required
def analyze():
    url = request.form.get("url", "").strip()

    if not url:
        flash("Please enter a URL to analyze.", "warning")
        return redirect(url_for("dashboard"))

    try:
        result = analyze_domain(url)
    except Exception:
        flash("Unable to analyze that URL. Please check the format and try again.", "danger")
        return redirect(url_for("dashboard"))

    search = SearchHistory(
        user_id=current_user.id,
        url=url,
        traffic=result["traffic"],
        global_rank=result["global_rank"],
        country_rank=result["country_rank"],
        category=result["category"],
    )

    try:
        db.session.add(search)
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash("There was a problem saving your search.", "danger")
        return redirect(url_for("dashboard"))

    flash(f"Analysis complete for {result['domain']}.", "success")
    return render_template("dashboard.html", **get_dashboard_context(result))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")





@app.route("/compare", methods=["GET", "POST"])
@login_required
def compare():
    if request.method == "POST":
        url1 = request.form.get("url1", "").strip()
        url2 = request.form.get("url2", "").strip()

        if not url1 or not url2:
            flash("Please enter two URLs to compare.", "warning")
            return render_template("compare.html")

        try:
            result1 = analyze_domain(url1)
            result2 = analyze_domain(url2)
        except Exception:
            flash("One or both URLs could not be analyzed.", "danger")
            return render_template("compare.html")

        return render_template(
            "compare.html", result1=result1, result2=result2
        )

    return render_template("compare.html")


@app.route("/export")
@login_required
def export_csv():
    history = SearchHistory.query.filter_by(user_id=current_user.id).all()
    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(["URL", "Traffic", "Global Rank", "Country Rank", "Category"])

    for item in history:
        writer.writerow(
            [
                item.url,
                item.traffic,
                item.global_rank,
                item.country_rank,
                item.category,
            ]
        )

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=analytics_report.csv"},
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )