# ⚡ TaskFlow AI — Smart Task Manager with Team Collaboration

> **Resume-ready, full-stack web application** built with Python Flask, SQLite, Bootstrap 5, and an AI-powered smart suggestion engine.

---

## 📸 Screenshots

> Login, Dashboard, Task Management, Team Collaboration, Notifications pages with a modern dark UI and cyan accent color scheme.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 Authentication | Register, Login, Logout with password hashing (Werkzeug) |
| 📊 Dashboard | Live stats: Total, Completed, Pending, Overdue tasks |
| ✅ Task CRUD | Create, Read, Update, Delete tasks with priority & deadline |
| 🤖 AI Suggestion | Rule-based AI suggests priority + deadline from task text |
| 👥 Team Collaboration | Create teams, invite members, assign & view shared tasks |
| 🔔 Notifications | Overdue alerts + due-soon warnings (3-day window) |
| 📎 File Uploads | Attach files to tasks (PNG, PDF, DOCX, ZIP…) |
| 🔍 Search & Filter | Search by keyword; filter by priority, status, deadline |
| 📄 Pagination | Task list paginated (8 per page) |
| 🌙 Dark / Light Mode | Toggle with localStorage persistence |
| 📱 Responsive | Fully mobile-friendly with collapsible sidebar |

---

## 🛠 Tech Stack

- **Backend:** Python 3.x · Flask 3.0
- **Database:** SQLite (via Python `sqlite3`)
- **Frontend:** HTML5 · CSS3 · Bootstrap 5.3 · Vanilla JS
- **Security:** Werkzeug password hashing · session management · file-type validation · parameterized SQL queries
- **Fonts:** Syne (display) · DM Sans (body) — Google Fonts

---

## 🗂 Folder Structure

```
project/
├── app.py              # Flask routes & AI logic
├── models.py           # DB init, schema, seeding
├── database.db         # SQLite database (auto-created)
├── requirements.txt
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── tasks.html
│   ├── create_task.html
│   ├── edit_task.html
│   ├── task_detail.html
│   ├── teams.html
│   ├── team_tasks.html
│   └── notifications.html
├── static/
│   ├── css/style.css
│   ├── js/script.js
│   └── uploads/        # User file attachments
└── README.md
```

---

## 🚀 Installation & Running Locally

### 1. Clone / Download the project

```bash
cd project
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate       # macOS / Linux
venv\Scripts\activate          # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python app.py
```

### 5. Open in browser

```
http://localhost:5000
```

---

## 👤 Demo Credentials

| Field    | Value      |
|----------|-----------|
| Username | `admin`    |
| Password | `admin123` |

---

## 🤖 How the AI Feature Works

When you type a task description in the **Create Task** form, the frontend calls `/api/suggest` (POST JSON) with the description text.

The rule-based engine scans for keywords:

| Keywords detected | Suggested Priority |
|---|---|
| urgent, asap, critical, blocker… | 🔴 High |
| someday, no rush, optional… | 🟢 Low |
| (default) | 🟡 Medium |

Deadline suggestions:

| Keyword | Suggested Deadline |
|---|---|
| today / due today | Today |
| tomorrow | Tomorrow |
| this week | +7 days |
| next week | +14 days |
| this month | +30 days |

Click **Apply** on the suggestion banner to auto-fill the Priority and Deadline fields.

---

## 🔒 Security

- Passwords hashed with `werkzeug.security.generate_password_hash`
- All DB queries use parameterized statements (SQL injection prevention)
- File uploads restricted to allowed extensions with `werkzeug.utils.secure_filename`
- Session timeout set to 2 hours
- Login required decorator on all protected routes

---

## 📄 Resume Description

> *Developed a full-stack AI-Powered Task Management System using Python Flask, SQLite, and Bootstrap 5. Implemented session-based authentication, RESTful API endpoints, team collaboration features, file attachment support, and a rule-based NLP engine that intelligently suggests task priority and deadlines based on natural language input.*

---

## 📝 License

MIT — free to use and modify.
