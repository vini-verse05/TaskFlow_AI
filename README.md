# ⚡ TaskFlow AI – Smart Task Manager

TaskFlow AI is a task management web application I built using Python Flask, SQLite, and Bootstrap. The idea was to create a simple place to manage personal tasks, keep track of deadlines, and collaborate with team members.

It also includes a small rule-based suggestion system that recommends task priorities and deadlines based on the description entered by the user.

## ✨ Features

- **User Authentication:** Register, log in, and log out with password hashing.
- **Dashboard:** View task statistics, including completed, pending, and overdue tasks.
- **Task Management:** Create, edit, view, and delete tasks with priorities and deadlines.
- **Smart Suggestions:** Get priority and deadline suggestions based on keywords in the task description.
- **Team Collaboration:** Create teams, work with team members, and view shared tasks.
- **Notifications:** Get alerts for overdue tasks and tasks approaching their deadlines.
- **File Attachments:** Upload supported files and attach them to tasks.
- **Search and Filters:** Find tasks by keyword, priority, status, or deadline.
- **Pagination:** Browse tasks in smaller, manageable lists.
- **Dark and Light Mode:** Switch between themes, with the preference saved locally.
- **Responsive UI:** Use the application on desktop and mobile screens.

## 🛠️ Tech Stack

| Area | Technologies |
|---|---|
| Backend | Python, Flask |
| Database | SQLite |
| Frontend | HTML, CSS, Bootstrap 5, JavaScript |
| Authentication | Flask sessions, Werkzeug password hashing |
| Task Suggestions | Python-based rule and keyword matching |
| File Handling | Flask file uploads and filename sanitization |

## 📁 Project Structure

```text
TaskFlow-AI/
├── app.py
├── models.py
├── requirements.txt
├── database.db           # Created locally
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
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   └── uploads/
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or a compatible Python 3 version
- pip

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd <project-folder>
```

Alternatively, download the repository and open its folder in VS Code.

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

On macOS or Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the application

```bash
python app.py
```

### 5. Open it in your browser

Visit:

```text
http://127.0.0.1:5000
```

The database should be initialized according to the application's database setup code.

## 🤖 How the Suggestion System Works

TaskFlow AI includes a rule-based suggestion feature to make task creation a little easier.

When a user enters a task description, the application checks for certain keywords and uses them to suggest a priority and deadline.

**Priority suggestions**

- **High:** Words such as `urgent`, `ASAP`, `critical`, or `blocker`
- **Low:** Words such as `someday`, `no rush`, or `optional`
- **Medium:** The default priority when no matching keyword is found

**Deadline suggestions**

- `today` → Today
- `tomorrow` → Tomorrow
- `this week` → Within 7 days
- `next week` → Within 14 days
- `this month` → Within 30 days

The user can apply the suggestions directly to the task form.

The system uses predefined rules and keyword matching rather than a trained machine learning model.

## 🔐 Security and Data Handling

The application includes several basic security measures:

- Password hashing using Werkzeug.
- Parameterized SQL queries for database operations.
- Filename sanitization and restrictions on supported upload extensions.
- Session-based authentication and a configured session lifetime.
- Login protection for restricted routes.

These measures provide a starting point for application security, although further validation and testing would be needed before deploying the application publicly.

## 💡 What I Learned

While working on TaskFlow AI, I explored how to connect a Flask backend with a database and a browser-based interface. I also worked with user authentication, task management, file uploads, and basic automation through a rule-based suggestion system.

The project helped me understand how different parts of a web application work together to support
