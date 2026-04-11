"""
seed_data.py — Populate TaskFlow AI with realistic mock data.

Run ONCE after starting the app for the first time:
    python seed_data.py

This adds:
  - 4 demo users
  - 3 teams
  - 25 tasks (various priorities, statuses, deadlines)
  - Team memberships
  - File attachment records
"""

import sqlite3
import os
from datetime import date, timedelta
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def seed():
    # ── Make sure tables exist ────────────────────────────────
    from models import init_db
    init_db()

    conn = get_db()
    cur  = conn.cursor()

    today = date.today()

    # ══════════════════════════════════════════════════════════
    # 1. USERS
    # ══════════════════════════════════════════════════════════
    users = [
        ("admin",   "admin@taskflow.io",   "admin123"),
        ("alice",   "alice@taskflow.io",   "alice123"),
        ("bob",     "bob@taskflow.io",     "bob123"),
        ("carol",   "carol@taskflow.io",   "carol123"),
    ]

    user_ids = {}
    for username, email, password in users:
        existing = cur.execute(
            "SELECT id FROM users WHERE username=?", (username,)
        ).fetchone()
        if existing:
            user_ids[username] = existing["id"]
            print(f"  [skip] user '{username}' already exists")
        else:
            cur.execute(
                "INSERT INTO users (username, email, password) VALUES (?,?,?)",
                (username, email, generate_password_hash(password))
            )
            user_ids[username] = cur.lastrowid
            print(f"  [+] user '{username}'")

    conn.commit()

    # ══════════════════════════════════════════════════════════
    # 2. TEAMS
    # ══════════════════════════════════════════════════════════
    teams_data = [
        ("Design Squad",    "admin"),
        ("Backend Ninjas",  "alice"),
        ("Product Guild",   "bob"),
    ]

    team_ids = {}
    for team_name, owner in teams_data:
        existing = cur.execute(
            "SELECT id FROM teams WHERE team_name=?", (team_name,)
        ).fetchone()
        if existing:
            team_ids[team_name] = existing["id"]
            print(f"  [skip] team '{team_name}' already exists")
        else:
            cur.execute(
                "INSERT INTO teams (team_name, created_by) VALUES (?,?)",
                (team_name, user_ids[owner])
            )
            team_ids[team_name] = cur.lastrowid
            print(f"  [+] team '{team_name}'")

    conn.commit()

    # ══════════════════════════════════════════════════════════
    # 3. TEAM MEMBERSHIPS
    # ══════════════════════════════════════════════════════════
    memberships = [
        # (team_name, username)
        ("Design Squad",   "admin"),
        ("Design Squad",   "alice"),
        ("Design Squad",   "carol"),
        ("Backend Ninjas", "alice"),
        ("Backend Ninjas", "bob"),
        ("Backend Ninjas", "admin"),
        ("Product Guild",  "bob"),
        ("Product Guild",  "carol"),
        ("Product Guild",  "admin"),
    ]

    for team_name, username in memberships:
        try:
            cur.execute(
                "INSERT INTO team_members (team_id, user_id) VALUES (?,?)",
                (team_ids[team_name], user_ids[username])
            )
        except sqlite3.IntegrityError:
            pass  # already a member

    conn.commit()
    print(f"  [+] team memberships set")

    # ══════════════════════════════════════════════════════════
    # 4. TASKS
    # ══════════════════════════════════════════════════════════
    # Helper: days offset from today
    def d(offset): return (today + timedelta(days=offset)).isoformat()

    tasks = [
        # (title, description, priority, deadline, status, owner, team_name_or_None)
        # ── Admin's tasks ──────────────────────────────────────
        (
            "Fix production login bug",
            "Users are being logged out randomly after 2 minutes. Investigate session handling in auth middleware. This is a critical blocker.",
            "High", d(-2), "Pending", "admin", None
        ),
        (
            "Update landing page copy",
            "Marketing has sent new copy for the hero section and feature highlights. Update all text and recheck SEO meta tags.",
            "Medium", d(3), "Pending", "admin", "Design Squad"
        ),
        (
            "Setup CI/CD pipeline",
            "Configure GitHub Actions for automated testing and deployment to staging. Also add Slack notifications on build status.",
            "High", d(1), "Pending", "admin", "Backend Ninjas"
        ),
        (
            "Conduct Q3 performance review",
            "Prepare slides and data for the quarterly performance review meeting. Include KPIs, velocity, and roadmap update.",
            "Medium", d(-5), "Completed", "admin", None
        ),
        (
            "Design new onboarding flow",
            "Create wireframes and high-fidelity mockups for the updated 3-step onboarding experience. Review with PM by EOW.",
            "High", d(5), "Pending", "admin", "Design Squad"
        ),
        (
            "Write unit tests for API",
            "Cover all endpoints in the tasks and teams modules. Aim for >80% coverage. Use pytest.",
            "Medium", d(7), "Pending", "admin", "Backend Ninjas"
        ),
        (
            "Archive old project files",
            "Move completed project assets from 2023 to the archive folder on S3. No rush, whenever possible.",
            "Low", d(30), "Pending", "admin", None
        ),
        (
            "Review pull request #42",
            "Bob submitted a PR for the new search feature. Review code, leave comments, and approve or request changes.",
            "High", d(0), "Completed", "admin", "Backend Ninjas"
        ),

        # ── Alice's tasks ──────────────────────────────────────
        (
            "Redesign dashboard cards",
            "Update the stat cards to use the new design tokens. Add subtle hover animations and improve mobile layout.",
            "Medium", d(4), "Pending", "alice", "Design Squad"
        ),
        (
            "Create icon set for mobile app",
            "Design 24 custom icons for the mobile navigation and action buttons. Export in SVG and PNG at 2x and 3x.",
            "Low", d(14), "Pending", "alice", "Design Squad"
        ),
        (
            "Database migration v2.1",
            "Run the pending Alembic migrations on staging. Verify data integrity after. ASAP before Monday deploy.",
            "High", d(-1), "Pending", "alice", "Backend Ninjas"
        ),
        (
            "Update API documentation",
            "Document all new endpoints added in sprint 14. Include request/response examples and error codes.",
            "Medium", d(10), "Pending", "alice", "Backend Ninjas"
        ),
        (
            "Prepare design system docs",
            "Document color tokens, typography scale, spacing rules, and component variants in Notion.",
            "Low", d(21), "Completed", "alice", "Design Squad"
        ),
        (
            "Optimize image assets",
            "Run all PNG/JPG assets through compression. Convert hero images to WebP. Target <200KB per image.",
            "Medium", d(6), "Pending", "alice", None
        ),

        # ── Bob's tasks ────────────────────────────────────────
        (
            "Define Q4 product roadmap",
            "Gather input from engineering and design leads. Prioritize features using the RICE scoring model. Present to stakeholders.",
            "High", d(2), "Pending", "bob", "Product Guild"
        ),
        (
            "User interview sessions",
            "Schedule and conduct 5 user interviews for the new task assignment feature. Document key insights.",
            "Medium", d(8), "Pending", "bob", "Product Guild"
        ),
        (
            "Fix pagination bug on tasks page",
            "Page 2 shows duplicate tasks when filters are active. Reproduce and fix the offset calculation in app.py.",
            "High", d(-3), "Completed", "bob", "Backend Ninjas"
        ),
        (
            "Set up error monitoring",
            "Integrate Sentry into the Flask app. Configure alerting for 5xx errors and slow requests (>2s).",
            "Medium", d(9), "Pending", "bob", "Backend Ninjas"
        ),
        (
            "Write blog post on AI features",
            "Draft a technical blog post explaining the smart task suggestion engine. Include code snippets and examples.",
            "Low", d(45), "Pending", "bob", None
        ),
        (
            "Team retrospective notes",
            "Compile and send out the Sprint 14 retrospective notes. Include action items and owners.",
            "Low", d(-10), "Completed", "bob", "Product Guild"
        ),

        # ── Carol's tasks ──────────────────────────────────────
        (
            "Audit accessibility compliance",
            "Run axe DevTools on all pages. Fix critical and serious WCAG 2.1 AA violations. Report results.",
            "High", d(3), "Pending", "carol", "Design Squad"
        ),
        (
            "Set up Google Analytics 4",
            "Migrate from UA to GA4. Configure custom events for task creation, team join, and file upload.",
            "Medium", d(7), "Pending", "carol", "Product Guild"
        ),
        (
            "Create email templates",
            "Design HTML email templates for welcome, password reset, and team invite notifications. Test in Litmus.",
            "Medium", d(12), "Pending", "carol", "Design Squad"
        ),
        (
            "Research competitor features",
            "Analyse Asana, Linear, and Notion task management features. Create comparison matrix and share with team.",
            "Low", d(20), "Pending", "carol", "Product Guild"
        ),
        (
            "Implement dark mode for mobile",
            "Apply CSS media query prefers-color-scheme to ensure mobile browsers honour system dark mode preference.",
            "Medium", d(-4), "Completed", "carol", "Design Squad"
        ),
    ]

    inserted = 0
    for (title, desc, priority, deadline, status, owner, team_name) in tasks:
        existing = cur.execute(
            "SELECT id FROM tasks WHERE title=? AND user_id=?",
            (title, user_ids[owner])
        ).fetchone()
        if existing:
            continue

        team_id = team_ids.get(team_name) if team_name else None
        cur.execute(
            """INSERT INTO tasks
               (title, description, priority, deadline, status, user_id, team_id)
               VALUES (?,?,?,?,?,?,?)""",
            (title, desc, priority, deadline, status, user_ids[owner], team_id)
        )
        inserted += 1

    conn.commit()
    print(f"  [+] {inserted} tasks inserted")

    # ══════════════════════════════════════════════════════════
    # 5. FAKE FILE ATTACHMENT RECORDS
    # ══════════════════════════════════════════════════════════
    # Attach dummy file records to the first 3 tasks of admin
    admin_tasks = cur.execute(
        "SELECT id FROM tasks WHERE user_id=? ORDER BY id LIMIT 3",
        (user_ids["admin"],)
    ).fetchall()

    fake_files = [
        ("bug_report.pdf",      "bug_report.pdf"),
        ("landing_copy_v2.docx","landing_copy_v2.docx"),
        ("ci_cd_plan.txt",      "ci_cd_plan.txt"),
    ]

    for i, task_row in enumerate(admin_tasks):
        fname, fpath = fake_files[i]
        existing = cur.execute(
            "SELECT id FROM files WHERE task_id=? AND filename=?",
            (task_row["id"], fname)
        ).fetchone()
        if not existing:
            cur.execute(
                "INSERT INTO files (task_id, file_path, filename) VALUES (?,?,?)",
                (task_row["id"], fpath, fname)
            )

    conn.commit()
    print(f"  [+] file attachment records added")

    conn.close()

    # ══════════════════════════════════════════════════════════
    print("\n✅  Mock data seeded successfully!")
    print("─" * 44)
    print("  Users:")
    for u, _, p in users:
        print(f"    {u:10s}  /  {p}")
    print("\n  Teams:")
    for t, o in teams_data:
        print(f"    {t}  (owner: {o})")
    print("\n  Tasks: 25 tasks across all users and teams")
    print("─" * 44)
    print("  Run:  python app.py   →  http://localhost:5000")


if __name__ == "__main__":
    seed()
