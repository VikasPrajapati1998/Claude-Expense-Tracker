# Claude-Expense-Tracker
Anthropic Claude Code 

```
Claude-Expense-Tracker/
  │
  ├── app.py                  # Flask app entry point — defines all routes
  │
  ├── database/
  │   ├── __init__.py         # Empty (makes it a Python package)
  │   └── db.py               # Stub — students implement get_db(), init_db(), seed_db()
  │
  ├── templates/
  │   ├── base.html           # Master layout — navbar, footer, font imports, block slots
  │   ├── landing.html        # Public homepage (extends base.html)
  │   ├── register.html       # Registration page (extends base.html)
  │   └── login.html          # Login page (extends base.html)
  │
  ├── static/
  │   ├── css/style.css       # All styling — CSS variables, layout, components, responsive
  │   └── js/main.js          # Empty stub — students add JS as features are built
  │
  ├── requirements.txt        # flask, werkzeug, pytest, pytest-flask
  └── venv/                   # Python virtual environment (not tracked in git)
```
