
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
- Quick genre links with live catalog counts.
- A nonce-based Content Security Policy, restrictive browser permissions and Django security headers.
- `sitemap.xml`, `robots.txt` and `/healthz/` routes for discovery and deployment checks.
- Django admin for maintaining the catalog.

The watchlist is stored in this browser's local storage. Clearing browser site data removes it.

## Quality checklist

### Productivity

1. Search titles from every page.
2. Search by genre.
3. Search by director.
4. Limit search input to 100 characters.
5. Filter by genre.
6. Filter by release year.
7. Set a minimum score.
8. Sort by release date, score, or title.
9. Clear all active filters quickly.
10. See a film count for every genre before browsing.
11. Jump directly to genre collections from the main navigation.
12. Browse popular picks.
13. Open the top-rated collection.
14. Get a random catalog pick.
15. Save, search, sort, export, remove, and randomly pick watchlist films.

### Security

1. Require a secret key outside development.
2. Keep debug off by default.
3. Restrict allowed hosts through deployment configuration.
4. Secure session cookies in production.
5. Secure CSRF cookies in production.
6. Redirect production requests to HTTPS.
7. Enable HSTS for production.
8. Disable MIME type sniffing.
9. Set a strict cross-origin referrer policy.
10. Isolate cross-origin windows.
11. Deny framing to reduce clickjacking risk.
12. Restrict scripts to same-origin files and a per-response nonce.
13. Block inline event-handler scripts.
14. Limit images and fonts to the catalog’s required sources.
15. Validate watchlist movie routes and poster hosts before using stored values.

### UI and accessibility

1. Add a keyboard skip link.
2. Keep one labeled main content landmark.
3. Label search and filter controls.
4. Mark the active collection in navigation.
5. Expose saved state with `aria-pressed`.
6. Announce watchlist changes politely.
7. Provide descriptive poster alternative text.
8. Show a local poster fallback when a remote image fails.
9. Keep interactive targets touch-friendly.
10. Use a two-column catalog layout on smaller screens.
11. Prevent horizontal overflow on narrow screens.
12. Show a clear empty state when filters find no films.
13. Preserve search and filter choices across pagination.
14. Respect reduced-motion preferences.
15. Keep visible focus rings on keyboard controls.

### Distinctive details

1. Use an asymmetric cinema-poster hero.
2. Keep the ink-black screening-room background.
3. Use one copper-gold accent throughout.
4. Frame the hero with a quiet projected-light wash.
5. Add thin film-reel rings behind the headline.
6. Animate the rings gently for motion-enabled users.
7. Reveal the hero copy with a short entrance.
8. Stagger catalog poster entrances.
9. Lift posters slightly on hover.
10. Brighten posters on focus as well as hover.
11. Animate the brand mark on hover.
12. Give genre links a compact poster-label feel.
13. Show genre counts directly on each link.
14. Use an editorial type scale for film titles.
15. Keep the watchlist private to the current device, with no tracking account.

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
