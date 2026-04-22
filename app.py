from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from functools import wraps

from flask import Flask, g, redirect, render_template, request, session, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_ROOT, "db", "student.db")

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-me-in-production"


# ---------------------------
# Database helpers
# ---------------------------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def table_has_column(table: str, column: str) -> bool:
    db = get_db()
    cur = db.execute(f"PRAGMA table_info({table})")
    return any(row["name"] == column for row in cur.fetchall())


def init_db():
    os.makedirs(os.path.join(APP_ROOT, "db"), exist_ok=True)
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            stud_id INTEGER UNIQUE,
            u_name TEXT UNIQUE,
            pass_hash TEXT,
            role TEXT,
            full_name TEXT,
            dept TEXT,
            cgpa REAL,
            created_at TEXT
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS company (
            company_id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            role_offered TEXT NOT NULL,
            min_cgpa REAL NOT NULL CHECK (min_cgpa <= 10 AND min_cgpa > 0),
            package REAL NOT NULL CHECK (package > 0)
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS applications (
            application_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            company_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            applied_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(student_id, company_id)
        )
        """
    )

    # Backfill missing columns if an old schema is present
    if not table_has_column("users", "full_name"):
        db.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
    if not table_has_column("users", "dept"):
        db.execute("ALTER TABLE users ADD COLUMN dept TEXT")
    if not table_has_column("users", "cgpa"):
        db.execute("ALTER TABLE users ADD COLUMN cgpa REAL")
    if not table_has_column("users", "created_at"):
        db.execute("ALTER TABLE users ADD COLUMN created_at TEXT")

    db.commit()


@app.before_request
def _ensure_db():
    init_db()


# ---------------------------
# Auth helpers
# ---------------------------

def admin_exists() -> bool:
    db = get_db()
    cur = db.execute("SELECT COUNT(*) AS cnt FROM users WHERE role = 'Admin'")
    return cur.fetchone()["cnt"] > 0


def login_required(role: str | None = None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("login"))
            if role and session.get("role") != role:
                return redirect(url_for("dashboard"))
            return fn(*args, **kwargs)

        return wrapper

    return decorator


# ---------------------------
# Routes
# ---------------------------

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    if not admin_exists():
        return redirect(url_for("setup"))
    return redirect(url_for("login"))


@app.route("/setup", methods=["GET", "POST"])
def setup():
    if admin_exists():
        return redirect(url_for("login"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        full_name = request.form.get("full_name", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            flash("Username and password are required.", "error")
        else:
            db = get_db()
            db.execute(
                "INSERT INTO users (u_name, pass_hash, role, full_name, created_at) VALUES (?, ?, 'Admin', ?, ?)",
                (username, generate_password_hash(password), full_name, datetime.utcnow().isoformat()),
            )
            db.commit()
            flash("Admin account created. Please sign in.", "success")
            return redirect(url_for("login"))
    return render_template("setup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        db = get_db()
        cur = db.execute("SELECT * FROM users WHERE u_name = ?", (username,))
        user = cur.fetchone()
        if not user:
            flash("No such user.", "error")
        elif not check_password_hash(user["pass_hash"], password):
            flash("Wrong password.", "error")
        else:
            session["user_id"] = user["user_id"]
            session["role"] = user["role"]
            session["username"] = user["u_name"]
            return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if not admin_exists():
        return redirect(url_for("setup"))
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        stud_id = request.form.get("stud_id", "").strip()
        dept = request.form.get("dept", "").strip()
        cgpa = request.form.get("cgpa", "").strip()
        if not (full_name and username and password and stud_id and dept and cgpa):
            flash("All fields are required.", "error")
        else:
            db = get_db()
            try:
                db.execute(
                    """
                    INSERT INTO users (stud_id, u_name, pass_hash, role, full_name, dept, cgpa, created_at)
                    VALUES (?, ?, ?, 'Student', ?, ?, ?, ?)
                    """,
                    (
                        int(stud_id),
                        username,
                        generate_password_hash(password),
                        full_name,
                        dept,
                        float(cgpa),
                        datetime.utcnow().isoformat(),
                    ),
                )
                db.commit()
                flash("Student registered. You can now log in.", "success")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("Username or student ID already exists.", "error")
    return render_template("register.html")


@app.route("/dashboard")
@login_required()
def dashboard():
    if session.get("role") == "Admin":
        return redirect(url_for("admin_dashboard"))
    return redirect(url_for("student_dashboard"))


# ---------------------------
# Admin views
# ---------------------------

@app.route("/admin")
@login_required("Admin")
def admin_dashboard():
    db = get_db()
    company_count = db.execute("SELECT COUNT(*) AS cnt FROM company").fetchone()["cnt"]
    student_count = db.execute("SELECT COUNT(*) AS cnt FROM users WHERE role = 'Student'").fetchone()["cnt"]
    application_count = db.execute("SELECT COUNT(*) AS cnt FROM applications").fetchone()["cnt"]
    return render_template(
        "admin_dashboard.html",
        company_count=company_count,
        student_count=student_count,
        application_count=application_count,
    )


@app.route("/admin/companies", methods=["GET", "POST"])
@login_required("Admin")
def admin_companies():
    db = get_db()
    if request.method == "POST":
        company_name = request.form.get("company_name", "").strip()
        role_offered = request.form.get("role_offered", "").strip()
        min_cgpa = request.form.get("min_cgpa", "").strip()
        package = request.form.get("package", "").strip()
        if not (company_name and role_offered and min_cgpa and package):
            flash("All company fields are required.", "error")
        else:
            db.execute(
                "INSERT INTO company (company_name, role_offered, min_cgpa, package) VALUES (?, ?, ?, ?)",
                (company_name, role_offered, float(min_cgpa), float(package)),
            )
            db.commit()
            flash("Company added.", "success")
    companies = db.execute("SELECT * FROM company ORDER BY company_name").fetchall()
    return render_template("companies.html", companies=companies, is_admin=True)


@app.route("/admin/students")
@login_required("Admin")
def admin_students():
    db = get_db()
    students = db.execute(
        "SELECT stud_id, u_name, full_name, dept, cgpa, created_at FROM users WHERE role = 'Student' ORDER BY full_name"
    ).fetchall()
    return render_template("students.html", students=students)


@app.route("/admin/applications", methods=["GET", "POST"])
@login_required("Admin")
def admin_applications():
    db = get_db()
    if request.method == "POST":
        app_id = request.form.get("application_id")
        status = request.form.get("status")
        if app_id and status:
            db.execute(
                "UPDATE applications SET status = ?, updated_at = ? WHERE application_id = ?",
                (status, datetime.utcnow().isoformat(), int(app_id)),
            )
            db.commit()
            flash("Application updated.", "success")

    companies = db.execute("SELECT company_id, company_name FROM company ORDER BY company_name").fetchall()
    selected_company = request.args.get("company_id", "")

    query = """
        SELECT a.application_id, a.status, a.applied_at, a.updated_at,
               u.full_name, u.u_name, u.stud_id, u.dept, u.cgpa,
               c.company_name, c.role_offered, c.package
        FROM applications a
        JOIN users u ON u.user_id = a.student_id
        JOIN company c ON c.company_id = a.company_id
        WHERE 1=1
    """
    params = []
    if selected_company:
        query += " AND c.company_id = ?"
        params.append(int(selected_company))
    query += " ORDER BY a.updated_at DESC"

    applications = db.execute(query, params).fetchall()
    return render_template(
        "applications.html",
        applications=applications,
        companies=companies,
        selected_company=selected_company,
    )


# ---------------------------
# Student views
# ---------------------------

@app.route("/student")
@login_required("Student")
def student_dashboard():
    db = get_db()
    student = db.execute("SELECT * FROM users WHERE user_id = ?", (session["user_id"],)).fetchone()
    app_count = db.execute(
        "SELECT COUNT(*) AS cnt FROM applications WHERE student_id = ?", (session["user_id"],)
    ).fetchone()["cnt"]
    offer_count = db.execute(
        "SELECT COUNT(*) AS cnt FROM applications WHERE student_id = ? AND status = 'Offered'",
        (session["user_id"],),
    ).fetchone()["cnt"]
    return render_template(
        "student_dashboard.html", student=student, app_count=app_count, offer_count=offer_count
    )


@app.route("/student/companies")
@login_required("Student")
def student_companies():
    db = get_db()
    student = db.execute("SELECT * FROM users WHERE user_id = ?", (session["user_id"],)).fetchone()
    companies = db.execute("SELECT * FROM company ORDER BY company_name").fetchall()
    applied = db.execute(
        "SELECT company_id FROM applications WHERE student_id = ?",
        (session["user_id"],),
    ).fetchall()
    applied_ids = {row["company_id"] for row in applied}
    return render_template(
        "companies.html",
        companies=companies,
        is_admin=False,
        student=student,
        applied_ids=applied_ids,
    )


@app.route("/student/apply/<int:company_id>", methods=["POST"])
@login_required("Student")
def apply_company(company_id: int):
    db = get_db()
    student = db.execute("SELECT * FROM users WHERE user_id = ?", (session["user_id"],)).fetchone()
    company = db.execute("SELECT * FROM company WHERE company_id = ?", (company_id,)).fetchone()
    if not company:
        flash("Company not found.", "error")
        return redirect(url_for("student_companies"))
    if student["cgpa"] is None or student["cgpa"] < company["min_cgpa"]:
        flash("You are not eligible for this company.", "error")
        return redirect(url_for("student_companies"))
    try:
        db.execute(
            """
            INSERT INTO applications (student_id, company_id, status, applied_at, updated_at)
            VALUES (?, ?, 'Applied', ?, ?)
            """,
            (session["user_id"], company_id, datetime.utcnow().isoformat(), datetime.utcnow().isoformat()),
        )
        db.commit()
        flash("Application submitted.", "success")
    except sqlite3.IntegrityError:
        flash("You already applied to this company.", "error")
    return redirect(url_for("student_companies"))


@app.route("/student/applications", methods=["GET", "POST"])
@login_required("Student")
def student_applications():
    db = get_db()
    if request.method == "POST":
        app_id = request.form.get("application_id")
        if app_id:
            db.execute(
                "UPDATE applications SET status = 'Accepted', updated_at = ? WHERE application_id = ? AND student_id = ?",
                (datetime.utcnow().isoformat(), int(app_id), session["user_id"]),
            )
            db.commit()
            flash("Offer accepted.", "success")

    applications = db.execute(
        """
        SELECT a.application_id, a.status, a.applied_at, a.updated_at,
               c.company_name, c.role_offered, c.package
        FROM applications a
        JOIN company c ON c.company_id = a.company_id
        WHERE a.student_id = ?
        ORDER BY a.updated_at DESC
        """,
        (session["user_id"],),
    ).fetchall()
    return render_template("student_applications.html", applications=applications)


if __name__ == "__main__":
    app.run(debug=True)
