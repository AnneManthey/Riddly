# Riddly

Riddly is an Advent calendar app with riddles behind its doors. It is built with Django and is currently an early-stage project. All users share the same set of up to 24 numbered doors, while each user's solved status, attempt count, and solve time are tracked independently.

## Quickstart

### Prerequisites

- Python

### Setup

From the project directory, create and activate a virtual environment, then install the pinned dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Apply the database migrations and start the development server:

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The project uses SQLite, configured in `core/settings.py`.

## Usage

Open `http://127.0.0.1:8000/` to log in. Accounts are managed in Django Admin; public registration is not available. After logging in, open `http://127.0.0.1:8000/dashboard/` to see the shared calendar.

Manage shared doors and the calendar's date restriction at `http://127.0.0.1:8000/admin/`. Date restrictions are disabled by default, leaving all doors open for testing. When enabled, door N unlocks on December N from 2026 onward; unlocked doors are available for the rest of December. Unsolved doors are locked again on January 1, while solved doors remain accessible. Each user's solve status, attempt count, and solve time are independent.
