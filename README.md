# Riddly

Riddly is an Advent calendar app with riddles behind its doors. It is built with Django and is currently an early-stage project. The app includes the initial login and calendar pages, while the calendar interface is still a placeholder. Its data model supports up to 24 numbered doors per user, with a riddle, solution, reward, and solved status for each door.

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
python manage.py runserver
```

The project uses SQLite, configured in `core/settings.py`.

## Usage

Open `http://127.0.0.1:8000/` for the login placeholder or `http://127.0.0.1:8000/dashboard/` for the calendar placeholder.
