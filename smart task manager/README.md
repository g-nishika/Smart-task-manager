# Team Task Manager

A full-stack team task management application built with Flask, SQLAlchemy, SQLite/PostgreSQL, Bootstrap, HTML, CSS, and JavaScript.

## Features

- Signup/Login/Logout with session-based authentication
- Password hashing with `werkzeug.security`
- Role-based access control: `ADMIN` and `MEMBER`
- Project and task management
- Task assignment and status tracking
- Dashboard statistics and responsive layout
- Seeded admin account and sample data

## Folder Structure

- `app.py` - Application entry point
- `models.py` - SQLAlchemy models and seed logic
- `routes/` - Authentication and dashboard routes
- `templates/` - HTML views
- `static/css/` - Custom styles
- `static/js/` - Page scripts

## Setup

1. Create a Python virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the application:

```powershell
python app.py
```

4. Open `http://127.0.0.1:5000`

## Default Admin Account

- Email: `admin@example.com`
- Password: `Admin@123`

## Using PostgreSQL or Railway

Set the `DATABASE_URL` environment variable before starting the app.

```powershell
$env:DATABASE_URL = "postgresql://user:password@host:port/dbname"
$env:SECRET_KEY = "your-production-secret"
python app.py
```

## Deployment Notes

- The app is ready for deployment on platforms like Railway.
- Use `DATABASE_URL` for PostgreSQL and set `SECRET_KEY`.
- For production, disable `debug` and use a WSGI server.
