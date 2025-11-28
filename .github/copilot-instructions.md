# eld - AI Agent Instructions

**eld** (Every Little Day) is a Django 5.1 holiday discovery & personal calendar web app with HTMX-powered zero-reload interactivity. This guide ensures AI agents understand the architecture, patterns, and workflows.

## Architecture Overview

### Core Components

1. **Holiday Database** (`apps/holidays/`)
   - Master source: 10+ APIs (Nager.Date, Calendarific, AbstractAPI, UN Observances)
   - Smart deduplication with fuzzy matching in `services/holiday_fetcher.py` and `services/deduplicator.py`
   - Celery Beat auto-refresh daily at 2 AM
   - Key models: `Holiday`, `Country`, `HolidayCategory`

2. **Personal Calendars** (`apps/calendars/`)
   - One-to-one user calendar with unique iCal feed token
   - `UserHoliday` model tracks saved holidays with reminder options
   - iCal feed generation for Google Calendar, Apple Calendar, Outlook via `views.py`
   - Key models: `UserCalendar`, `UserHoliday`

3. **User Accounts** (`apps/accounts/`)
   - Django-Allauth with email + Google/GitHub/Apple OAuth
   - Auto-creates `UserCalendar` on signup with unique `feed_token`

### Data Flow

```
External APIs → HolidayFetcher → Deduplicator → Holiday Model → Discovery Views
                                                                  ↓
User (HTMX Click) → Toggle UserHoliday → iCal Feed → Calendar Export
```

## Key Patterns & Conventions

### 1. HTMX Integration
- **Every interactive element** uses HTMX (no page reloads)
- All views have HTMX variants that return HTML partials
- Examples: `week_view()`, `month_view()`, `apply_filters()` in `apps/holidays/views.py`
- Partials stored in `templates/holidays/partials/`

### 2. Django Best Practices
- **Thin views**, business logic in `services/` modules
- **select_related/prefetch_related** on all multi-join queries (avoid N+1)
- **Database indexes** on frequently filtered fields: `date`, `year`, `is_global`, `feed_token`
- Management commands for admin tasks: `seed_holidays`, `refresh_holidays`

### 3. Celery + Redis
- **Shared task**: `refresh_all_holidays()` runs daily (Celery Beat schedule in `settings.py`)
- Refreshes current year + next 2 years
- Redis cache for filters to enable instant HTMX responses
- Flower monitoring dashboard at `:5555`

### 4. Authentication & Authorization
- Login required for calendar adds (except viewing)
- Unique `feed_token` makes calendars shareable without exposing user ID
- Social OAuth set up in `INSTALLED_APPS` with provider-specific callbacks

### 5. Frontend Stack
- **Tailwind CSS** with celebration theme (purple, pink, orange, blue, green)
- **Alpine.js** for minimal reactive components (dark mode toggle, etc.)
- **Canvas Confetti** on fun holiday saves
- **Mobile-first** responsive (sm/md/lg breakpoints in `tailwind.config.js`)

## Development Workflows

### Local Development
```bash
chmod +x start.sh
./start.sh
# Starts: Django (8000), PostgreSQL, Redis, Celery worker, Celery Beat, Flower (5555)
```

### Database Migrations
```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

### Seed/Refresh Holiday Data
```bash
docker-compose exec web python manage.py seed_holidays  # Initial import
docker-compose exec web python manage.py refresh_holidays  # Update all sources
```

### Admin Interface
- Access `/admin` with superuser
- Bulk import/export holidays
- Inline category editing
- Monitor user calendars and saved holidays

### Testing Holiday Discovery
- `/` - Home page
- `/discover/` - Main discovery view (HTMX-powered filters)
- `/discover/week/` - Next 7 days (HTMX partial)
- `/calendar/feed/{feed_token}/` - iCal feed (webcal:// for calendar apps)

## Critical Configuration

### settings.py
- `INSTALLED_APPS`: holidays, calendars, accounts (local apps) + allauth + django_htmx + django_celery_beat
- `ALLOWED_HOSTS`: Set via environment variable
- `CELERY_BEAT_SCHEDULE`: Daily refresh at 2 AM UTC
- `CACHES`: Redis for filter optimization
- Environment-driven: DEBUG, SECRET_KEY, DATABASE_URL, REDIS_URL, CELERY_BROKER_URL

### Environment Variables (.env)
```
DEBUG=False
SECRET_KEY=<generate-strong-key>
DATABASE_URL=postgresql://user:pass@host:5432/eld_db
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=$REDIS_URL
CELERY_RESULT_BACKEND=$REDIS_URL
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SITE_URL=https://yourdomain.com  # For feed_url generation
```

### Database Indexes
- `Holiday`: date, year, is_global (multi-column index)
- `UserCalendar`: feed_token (unique + indexed)
- `Country`: code (unique + indexed for lookups)

## Common Tasks

### Add a New Holiday Data Source
1. Update `HolidayFetcher.fetch_all_holidays()` in `apps/holidays/services/holiday_fetcher.py`
2. Add API call with error handling
3. Return list of dicts: `{name, date, countries, categories, sources, external_id}`
4. Deduplicator automatically handles duplicates

### Add Discovery Filter
1. Update `apply_filters()` in `apps/holidays/views.py`
2. Add new GET param logic: `request.GET.get('filter_name')`
3. Create partial template in `templates/holidays/partials/`
4. Update discovery.html HTMX call to include new filter

### Modify Reminder Logic
1. Update `UserHoliday` model if new reminder type needed
2. Add Celery task in `apps/holidays/tasks.py`
3. Schedule in `CELERY_BEAT_SCHEDULE` (settings.py)

### Deploy to Production
- See `DEPLOYMENT.md` for Railway, Render, DigitalOcean guides
- Key: Migrate, seed data, set env vars, run Celery worker + beat separately
- Use strong SECRET_KEY generator
- Set DEBUG=False

## File Structure Map

| Path | Purpose |
|------|---------|
| `apps/holidays/models.py` | Holiday, Country, Category models with indexes |
| `apps/holidays/views.py` | Discovery views (week/month/year) with HTMX partials |
| `apps/holidays/services/holiday_fetcher.py` | 10+ API integrations |
| `apps/holidays/services/deduplicator.py` | Fuzzy duplicate detection |
| `apps/holidays/tasks.py` | Celery tasks (refresh_all_holidays) |
| `apps/calendars/models.py` | UserCalendar, UserHoliday with feed_token |
| `apps/calendars/views.py` | iCal feed generation (.ics format) |
| `templates/holidays/discovery.html` | Main discovery UI with HTMX |
| `templates/holidays/partials/` | HTMX response partials (holiday_list.html, etc.) |
| `docker-compose.yml` | Local dev stack: PostgreSQL, Redis, Celery, Flower |
| `settings.py` | Django config, Celery Beat schedule, Redis cache |

## Performance Considerations

- **Query Optimization**: All holiday fetches use `prefetch_related('countries', 'categories')`
- **Caching**: Filter results cached in Redis for instant HTMX responses
- **Indexing**: Multi-column index on (date, is_global) for discovery queries
- **Pagination**: Implement if holiday count exceeds 1000 per view
- **N+1 Prevention**: Always use select/prefetch_related on related models

## Conventions to Follow

- **Commit messages**: `feat(scope): description` per CONTRIBUTING.md
- **Code style**: PEP 8, 4-space indent, 100 char line limit
- **Docstrings**: Function/class docstrings with Args/Returns (see tasks.py)
- **Model fields**: Always include `db_index=True` on frequently filtered columns
- **Template naming**: Use `_` prefix for partials (e.g., `_holiday_card.html`)
- **Celery tasks**: Use `@shared_task` decorator, log progress, handle errors

## Quick Debugging Tips

1. **Missing holidays**: Run `python manage.py refresh_holidays` to reseed
2. **Calendar feed not syncing**: Check `UserCalendar.feed_token` generation in model `save()`
3. **HTMX filter delays**: Check Redis connection and cache config
4. **Celery tasks stuck**: Monitor Flower at `:5555` or check Redis with `redis-cli`
5. **CSS not loading**: Run `python manage.py collectstatic --noinput` and check Whitenoise config

---

**Last Updated**: 2025-01-01  
For project details, see `PROJECT_SUMMARY.md`, `README.md`, `CONTRIBUTING.md`, `DEPLOYMENT.md`
