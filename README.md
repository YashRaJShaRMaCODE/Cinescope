
# Cinescope

Cinescope is a Django-based movie discovery web app. It provides pages for browsing movies, viewing details, and filtering by genre, director, rating, release year, and curated lists such as top rated, upcoming, popular, and random picks.

## Features

- Home page listing all movies.
- Movie detail page.
- Search by movie title.
- Filter and browse by:
  - Genre
  - Director
  - Minimum rating
  - Release year
- Curated pages:
  - Top rated
  - Upcoming releases
  - Popular movies
  - Random selection
- Django admin panel for managing data.

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
pip install django
```

### 4) Apply migrations

```bash
python manage.py migrate
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
- `/admin/` – Django admin

## Notes

- The project currently uses SQLite for local development.
- Ensure Django is installed in your active environment before running management commands.
