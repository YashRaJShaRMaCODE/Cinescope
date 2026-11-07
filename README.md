
# CineScope

CineScope is a Django movie discovery catalog. Browse titles by genre, release year, director and catalog score, then open a film page for its details and related picks.

**Live site:** [cinescope-3pc5.onrender.com](https://cinescope-3pc5.onrender.com/)

## Features

- Search titles, genres and directors.
- Filter the catalog by genre, release year and minimum score; sort by release date, score or title.
- Browse popular, top-rated, upcoming and random collections.
- Open movie pages with poster fallback, catalog details, related films, canonical metadata and Movie structured data.
- Save films to a private, device-local watchlist; no account or server-side activity tracking is needed.
- Ask CineScope to pick a random film from your saved list, then open that film directly.
- Responsive poster-first layout, keyboard-accessible controls, reduced-motion support and lazy-loaded images.
- `sitemap.xml`, `robots.txt` and `/healthz/` routes for discovery and deployment checks.
- Django admin for maintaining the catalog.

The watchlist is stored in this browser's local storage. Clearing browser site data removes it.

## Tech Stack

- Python
- Django
- SQLite (default local database)
- Django templates + static assets

## Project Structure

- `Cinescope/` – Django project configuration (`settings.py`, `urls.py`, `wsgi.py`, `asgi.py`)
- `home/` – Main Django app containing models, views, and routes
- `templates/` – HTML templates for all views
- `static/` – Static files
- `manage.py` – Django management entrypoint

## Getting Started

### 1) Clone repository

```bash
git clone <your-repo-url>
cd Cinescope
```

### 2) Create and activate virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Apply migrations

```powershell
$env:DJANGO_SECRET_KEY = "local-development-only"
$env:DJANGO_DEBUG = "true"
```

On macOS/Linux, use `export` for those variables. Then:

```bash
python manage.py migrate
python manage.py seed_movies
```

### 5) Run development server

```bash
python manage.py runserver
```

Open: <http://127.0.0.1:8000/>

## URL Endpoints

- `/` – Home
- `/movie/<id>/` – Movie detail
- `/search/?q=<query>` – Search results
- `/genre/<genre_name>/` – Genre listing
- `/director/<director_name>/` – Director listing
- `/rating/<rating_value>/` – Movies with rating greater than or equal to value
- `/release-year/<year>/` – Movies by release year
- `/top-rated/` – Top 10 rated movies
- `/upcoming/` – Upcoming releases
- `/popular/` – Popular movies
- `/random/` – Random picks
- `/robots.txt` and `/sitemap.xml` – Search discovery
- `/healthz/` – Service health
- `/admin/` – Django admin

## Notes

- SQLite is used for the seeded catalog. Keep user-submitted content off this deployment until a persistent database is configured.
- Render runs migrations and idempotently seeds the sample catalog during deploy; `/healthz/` is the configured health check.
- GitHub Actions runs the Django checks and test suite. Dependabot checks Python and workflow dependencies weekly.
