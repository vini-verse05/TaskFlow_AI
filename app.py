"""
app.py — Main Flask application for AI-Powered Smart Task Manager
with Team Collaboration.

Run:
    pip install -r requirements.txt
    python app.py
"""

import os
import re
from datetime import datetime, date, timedelta
from functools import wraps

from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash, jsonify, send_from_directory)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from models import get_db, init_db

# ── App Configuration ──────────────────────────────────────────────────────
app = Flask(__name__)
# NEW — add this
import os
from dotenv import load_dotenv

load_dotenv()  # loads variables from .env file

app.secret_key = os.environ.get("SECRET_KEY", "fallback-dev-key-change-me")

UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf", "doc", "docx", "txt", "zip"}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=2)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── Helpers ────────────────────────────────────────────────────────────────

def login_required(f):
    """Decorator: redirect to login if not authenticated."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def ai_suggest_priority(text: str) -> str:
    """
    Rule-based AI: analyse keywords in the task description
    and return a suggested priority (High / Medium / Low).
    """
    text_lower = text.lower()
    high_keywords = [
        "urgent", "asap", "immediately", "critical", "emergency",
        "deadline today", "due today", "important", "high priority",
        "fix now", "production issue", "blocker", "hotfix"
    ]
    low_keywords = [
        "someday", "whenever", "low priority", "eventually",
        "no rush", "optional", "nice to have", "backlog"
    ]
    if any(kw in text_lower for kw in high_keywords):
        return "High"
    if any(kw in text_lower for kw in low_keywords):
        return "Low"
    return "Medium"


def ai_suggest_deadline(text: str) -> str | None:
    """
    Rule-based AI: suggest a deadline offset from today
    based on keywords found in the description.
    """
    text_lower = text.lower()
    today = date.today()
    if any(kw in text_lower for kw in ["today", "due today", "deadline today"]):
        return today.isoformat()
    if any(kw in text_lower for kw in ["tomorrow", "by tomorrow"]):
        return (today + timedelta(days=1)).isoformat()
    if re.search(r"\bthis week\b|\bend of week\b", text_lower):
        return (today + timedelta(days=7)).isoformat()
    if re.search(r"\bnext week\b", text_lower):
        return (today + timedelta(days=14)).isoformat()
    if re.search(r"\bthis month\b|\bend of month\b", text_lower):
        return (today + timedelta(days=30)).isoformat()
    return None


# ── Auth Routes ────────────────────────────────────────────────────────────

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")

        # Validation
        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html")
        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("register.html")

        db = get_db()
        existing = db.execute(
            "SELECT id FROM users WHERE username=? OR email=?", (username, email)
        ).fetchone()
        if existing:
            flash("Username or email already taken.", "danger")
            db.close()
            return render_template("register.html")

        db.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, generate_password_hash(password))
        )
        db.commit()
        db.close()
        flash("Account created! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username=?", (username,)
        ).fetchone()
        db.close()

        if user and check_password_hash(user["password"], password):
            session.permanent = True
            session["user_id"]  = user["id"]
            session["username"] = user["username"]
            flash(f"Welcome back, {user['username']}!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# ── Dashboard ──────────────────────────────────────────────────────────────

@app.route("/dashboard")
@login_required
def dashboard():
    db  = get_db()
    uid = session["user_id"]
    today = date.today().isoformat()

    total     = db.execute("SELECT COUNT(*) FROM tasks WHERE user_id=?", (uid,)).fetchone()[0]
    completed = db.execute("SELECT COUNT(*) FROM tasks WHERE user_id=? AND status='Completed'", (uid,)).fetchone()[0]
    pending   = db.execute("SELECT COUNT(*) FROM tasks WHERE user_id=? AND status='Pending'", (uid,)).fetchone()[0]
    overdue   = db.execute(
        "SELECT COUNT(*) FROM tasks WHERE user_id=? AND status!='Completed' AND deadline < ?",
        (uid, today)
    ).fetchone()[0]

    recent_tasks = db.execute(
        "SELECT * FROM tasks WHERE user_id=? ORDER BY created_at DESC LIMIT 5", (uid,)
    ).fetchall()

    # Due-soon: tasks due within next 3 days (not completed)
    due_soon_date = (date.today() + timedelta(days=3)).isoformat()
    due_soon = db.execute(
        """SELECT * FROM tasks WHERE user_id=? AND status!='Completed'
           AND deadline IS NOT NULL AND deadline >= ? AND deadline <= ?
           ORDER BY deadline""",
        (uid, today, due_soon_date)
    ).fetchall()

    db.close()
    return render_template("dashboard.html",
        total=total, completed=completed, pending=pending,
        overdue=overdue, recent_tasks=recent_tasks, due_soon=due_soon
    )


# ── Task CRUD ──────────────────────────────────────────────────────────────

@app.route("/tasks")
@login_required
def tasks():
    db  = get_db()
    uid = session["user_id"]

    search   = request.args.get("search", "").strip()
    priority = request.args.get("priority", "")
    status   = request.args.get("status", "")
    deadline = request.args.get("deadline", "")
    page     = int(request.args.get("page", 1))
    per_page = 8

    query  = "SELECT * FROM tasks WHERE user_id=?"
    params = [uid]

    if search:
        query += " AND (title LIKE ? OR description LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    if priority:
        query += " AND priority=?"
        params.append(priority)
    if status:
        query += " AND status=?"
        params.append(status)
    if deadline:
        query += " AND deadline=?"
        params.append(deadline)

    total_count = db.execute(
        query.replace("SELECT *", "SELECT COUNT(*)"), params
    ).fetchone()[0]

    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params += [per_page, (page - 1) * per_page]

    task_list = db.execute(query, params).fetchall()
    db.close()

    total_pages = (total_count + per_page - 1) // per_page
    return render_template("tasks.html",
        tasks=task_list, page=page, total_pages=total_pages,
        search=search, priority=priority, status=status, deadline=deadline
    )


@app.route("/tasks/create", methods=["GET", "POST"])
@login_required
def create_task():
    db  = get_db()
    uid = session["user_id"]

    # Fetch user's teams for assignment
    teams = db.execute(
        """SELECT t.* FROM teams t
           JOIN team_members tm ON t.id=tm.team_id
           WHERE tm.user_id=?""", (uid,)
    ).fetchall()

    if request.method == "POST":
        title       = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        priority    = request.form.get("priority", "Medium")
        deadline    = request.form.get("deadline", "") or None
        team_id     = request.form.get("team_id") or None
        assigned_to = request.form.get("assigned_to") or None

        if not title:
            flash("Task title is required.", "danger")
            return render_template("create_task.html", teams=teams)

        db.execute(
            """INSERT INTO tasks (title, description, priority, deadline, user_id, team_id, assigned_to)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (title, description, priority, deadline, uid, team_id, assigned_to)
        )
        db.commit()

        # Handle file upload
        file = request.files.get("attachment")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            task_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
            db.execute(
                "INSERT INTO files (task_id, file_path, filename) VALUES (?, ?, ?)",
                (task_id, filename, filename)
            )
            db.commit()

        db.close()
        flash("Task created successfully!", "success")
        return redirect(url_for("tasks"))

    db.close()
    return render_template("create_task.html", teams=teams)


@app.route("/tasks/<int:task_id>")
@login_required
def task_detail(task_id):
    db  = get_db()
    uid = session["user_id"]
    task = db.execute("SELECT * FROM tasks WHERE id=? AND user_id=?", (task_id, uid)).fetchone()
    if not task:
        flash("Task not found.", "danger")
        return redirect(url_for("tasks"))

    files = db.execute("SELECT * FROM files WHERE task_id=?", (task_id,)).fetchall()
    assigned_user = None
    if task["assigned_to"]:
        assigned_user = db.execute(
            "SELECT username FROM users WHERE id=?", (task["assigned_to"],)
        ).fetchone()

    db.close()
    return render_template("task_detail.html", task=task, files=files, assigned_user=assigned_user)


@app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    db  = get_db()
    uid = session["user_id"]
    task = db.execute("SELECT * FROM tasks WHERE id=? AND user_id=?", (task_id, uid)).fetchone()
    if not task:
        flash("Task not found.", "danger")
        return redirect(url_for("tasks"))

    teams = db.execute(
        """SELECT t.* FROM teams t
           JOIN team_members tm ON t.id=tm.team_id WHERE tm.user_id=?""", (uid,)
    ).fetchall()

    if request.method == "POST":
        title       = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        priority    = request.form.get("priority", "Medium")
        deadline    = request.form.get("deadline") or None
        status      = request.form.get("status", "Pending")

        if not title:
            flash("Task title is required.", "danger")
            return render_template("edit_task.html", task=task, teams=teams)

        db.execute(
            """UPDATE tasks SET title=?, description=?, priority=?,
               deadline=?, status=? WHERE id=?""",
            (title, description, priority, deadline, status, task_id)
        )
        db.commit()
        db.close()
        flash("Task updated!", "success")
        return redirect(url_for("tasks"))

    db.close()
    return render_template("edit_task.html", task=task, teams=teams)


@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    db  = get_db()
    uid = session["user_id"]
    db.execute("DELETE FROM tasks WHERE id=? AND user_id=?", (task_id, uid))
    db.execute("DELETE FROM files WHERE task_id=?", (task_id,))
    db.commit()
    db.close()
    flash("Task deleted.", "info")
    return redirect(url_for("tasks"))


@app.route("/tasks/<int:task_id>/complete", methods=["POST"])
@login_required
def complete_task(task_id):
    db  = get_db()
    uid = session["user_id"]
    db.execute(
        "UPDATE tasks SET status='Completed' WHERE id=? AND user_id=?", (task_id, uid)
    )
    db.commit()
    db.close()
    flash("Task marked as completed!", "success")
    return redirect(url_for("tasks"))


# ── AI Suggestion API ──────────────────────────────────────────────────────

@app.route("/api/suggest", methods=["POST"])
@login_required
def api_suggest():
    """Return AI-suggested priority and deadline for a task description."""
    data = request.get_json(force=True)
    text = data.get("text", "")
    return jsonify({
        "priority": ai_suggest_priority(text),
        "deadline": ai_suggest_deadline(text)
    })


# ── Teams ──────────────────────────────────────────────────────────────────

@app.route("/teams")
@login_required
def teams():
    db  = get_db()
    uid = session["user_id"]

    my_teams = db.execute(
        """SELECT t.*, u.username as creator_name,
                  (SELECT COUNT(*) FROM team_members WHERE team_id=t.id) as member_count
           FROM teams t JOIN users u ON t.created_by=u.id
           JOIN team_members tm ON t.id=tm.team_id
           WHERE tm.user_id=?
           ORDER BY t.created_at DESC""",
        (uid,)
    ).fetchall()

    db.close()
    return render_template("teams.html", teams=my_teams)


@app.route("/teams/create", methods=["POST"])
@login_required
def create_team():
    db        = get_db()
    uid       = session["user_id"]
    team_name = request.form.get("team_name", "").strip()

    if not team_name:
        flash("Team name is required.", "danger")
        return redirect(url_for("teams"))

    db.execute("INSERT INTO teams (team_name, created_by) VALUES (?, ?)", (team_name, uid))
    team_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    db.execute("INSERT INTO team_members (team_id, user_id) VALUES (?, ?)", (team_id, uid))
    db.commit()
    db.close()
    flash(f"Team '{team_name}' created!", "success")
    return redirect(url_for("teams"))


@app.route("/teams/<int:team_id>/invite", methods=["POST"])
@login_required
def invite_member(team_id):
    db       = get_db()
    uid      = session["user_id"]
    username = request.form.get("username", "").strip()

    # Verify current user is in this team
    member = db.execute(
        "SELECT id FROM team_members WHERE team_id=? AND user_id=?", (team_id, uid)
    ).fetchone()
    if not member:
        flash("Unauthorized.", "danger")
        db.close()
        return redirect(url_for("teams"))

    invite_user = db.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
    if not invite_user:
        flash(f"User '{username}' not found.", "danger")
    else:
        try:
            db.execute(
                "INSERT INTO team_members (team_id, user_id) VALUES (?, ?)",
                (team_id, invite_user["id"])
            )
            db.commit()
            flash(f"'{username}' added to team!", "success")
        except Exception:
            flash("User is already in the team.", "warning")

    db.close()
    return redirect(url_for("teams"))


@app.route("/teams/<int:team_id>/tasks")
@login_required
def team_tasks(team_id):
    db  = get_db()
    uid = session["user_id"]

    # Ensure user is a member
    member = db.execute(
        "SELECT id FROM team_members WHERE team_id=? AND user_id=?", (team_id, uid)
    ).fetchone()
    if not member:
        flash("Access denied.", "danger")
        return redirect(url_for("teams"))

    team = db.execute("SELECT * FROM teams WHERE id=?", (team_id,)).fetchone()
    task_list = db.execute(
        """SELECT t.*, u.username as owner_name
           FROM tasks t JOIN users u ON t.user_id=u.id
           WHERE t.team_id=? ORDER BY t.created_at DESC""",
        (team_id,)
    ).fetchall()

    db.close()
    return render_template("team_tasks.html", team=team, tasks=task_list)


# ── Notifications ──────────────────────────────────────────────────────────

@app.route("/notifications")
@login_required
def notifications():
    db    = get_db()
    uid   = session["user_id"]
    today = date.today().isoformat()
    soon  = (date.today() + timedelta(days=3)).isoformat()

    overdue = db.execute(
        """SELECT * FROM tasks WHERE user_id=? AND status!='Completed'
           AND deadline IS NOT NULL AND deadline < ?
           ORDER BY deadline""",
        (uid, today)
    ).fetchall()

    due_soon = db.execute(
        """SELECT * FROM tasks WHERE user_id=? AND status!='Completed'
           AND deadline IS NOT NULL AND deadline >= ? AND deadline <= ?
           ORDER BY deadline""",
        (uid, today, soon)
    ).fetchall()

    db.close()
    return render_template("notifications.html", overdue=overdue, due_soon=due_soon)


# ── File Download ──────────────────────────────────────────────────────────

@app.route("/uploads/<path:filename>")
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# ── Run ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
