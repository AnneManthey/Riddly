# Riddly

Riddly is a Django-based Advent calendar where users solve riddles hidden behind up to 24 numbered doors. Everyone sees the same doors, while each user's answers, attempts, and solve times are tracked independently. Accounts are managed through Django Admin; there is no public registration. The app also includes a web app manifest for installation on supported browsers.

## Quickstart

### Prerequisites

- Python 3.14
- PowerShell (commands below use PowerShell syntax)

### Setup

From the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DJANGO_DEBUG = "1"
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/` and sign in with a Django user account. The local development setting uses SQLite at `db.sqlite3` by default.

## Usage

- Open `/dashboard/` to view the calendar after signing in.
- Use `/admin/` to create and manage shared doors and configure calendar date restrictions.
- The login page's optional **Stay signed in** checkbox keeps the Django session active for up to 30 days since the last activity. Without it, the session ends when the browser closes.
- Date restrictions are disabled by default. When enabled, door N unlocks on December N from 2026 onward. Unsolved doors lock again on January 1; solved doors remain accessible.

## Android installation

Riddly includes a web app manifest for installation through Chrome on Android. The installed app opens the dashboard and redirects unauthenticated users to the login page. It requires an internet connection and does not cache pages or save answers offline.

To install it on a phone, deploy the app at the root of an HTTPS address reachable from the phone and serve the collected static files from the same origin, including `manifest.webmanifest` and its icons. Serve the manifest as `application/manifest+json` or `application/json`, then open the app in Chrome and use the browser's install or "Add to Home screen" option. Availability and wording depend on the browser. The current app icons are provisional and derived from the existing favicon.

## Configuration

- `DJANGO_DEBUG`: set to `1` for local development. It defaults to `0`.
- `DJANGO_SECRET_KEY`: required when `DJANGO_DEBUG` is not `1`.
- `DJANGO_ALLOWED_HOSTS`: comma-separated allowed host names; defaults to an empty list.
- `DJANGO_CSRF_TRUSTED_ORIGINS`: comma-separated trusted origins; defaults to an empty list.
- `DJANGO_DB_PATH`: optional SQLite database path; defaults to `db.sqlite3` in the project directory.

## Tests

With the virtual environment activated and `DJANGO_DEBUG` set to `1`, run:

```powershell
python manage.py test
```
