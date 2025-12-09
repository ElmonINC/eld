# 🎉 eld - Every Little Day

**The world's most beautiful, complete, and joyful public holiday discovery + personal calendar app.**

Discover public holidays, religious observances, UN international days, and fun celebrations from 195+ countries. One click adds them to your personal calendar. Export to Google Calendar, Apple Calendar, or download as .ics.

![eld Hero](https://via.placeholder.com/1200x600/8B5CF6/FFFFFF?text=eld+-+Every+Celebration+Matters)

## Tech Stack

### Backend
- **Python 3.12** - Modern Python
- **Django 5.1+** - Web framework
- **PostgreSQL 16** - Database
- **Celery + Redis** - Background tasks
- **Celery Beat** - Scheduled jobs

### Frontend
- **Django Templates** - Server-side rendering
- **HTMX 2.0** - Zero-JS interactivity
- **Alpine.js** - Tiny reactive components
- **Tailwind CSS 3.4+** - Utility-first styling
- **Canvas Confetti** - Celebration animations

### Authentication
- **Django-Allauth** - Email + social login
- **Google OAuth**
- **GitHub OAuth**
- **Apple OAuth**

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Whitenoise** - Static file serving
- **Gunicorn** - Production WSGI server

## Usage Guide

### Discovering Holidays

1. **Browse** - Choose your view (Week, Month, or Year)
2. **Filter** - Select country, category, or search
3. **Click** - Add any holiday to your calendar instantly
4. **Celebrate** - Watch confetti for fun holidays! 🎊

### Managing Your Calendar

1. **View "My Calendar"** - See all your saved holidays
2. **Export Options:**
   - Click "Google Calendar" → Auto-subscribe
   - Click "Apple Calendar" → Opens in Calendar app
   - Click "Download .ics" → Save file locally
3. **Set Reminders** - Get notified 1 day before or morning of

### Admin Features

Access `/admin` to:
- **Manage holidays** - Edit, verify, bulk actions
- **Add countries** - New regions and flags
- **Create categories** - Custom holiday types
- **View users** - Monitor signups and usage

## Management Commands

### Seed Initial Data
```bash
python manage.py seed_holidays
```
Imports holidays for 2025-2027 from all sources.

### Refresh Holiday Data
```bash
python manage.py refresh_holidays
```
Fetch latest holidays from all 10+ sources.

### Refresh Specific Year
```bash
python manage.py refresh_holidays --year 2026
```

## Design Philosophy

**Celebration-First:**
- Every interaction should spark joy
- Colors are vibrant and playful
- Animations celebrate user actions
- Dark mode for late-night planning

**Zero Friction:**
- No page reloads (HTMX magic)
- One-click actions
- Instant filters
- Mobile-first responsive

**Data Quality:**
- 10+ sources ensure completeness
- Smart deduplication prevents noise
- Daily updates keep it fresh
- Admin tools for curation

## Project Structure

```
eld/
├── apps/
│   ├── holidays/          # Holiday models, views, services
│   │   ├── services/      # API fetchers, deduplicator
│   │   ├── management/    # Commands (seed, refresh)
│   │   └── tasks.py       # Celery tasks
│   ├── calendars/         # User calendars, iCal feeds
│   └── accounts/          # User profiles
├── templates/             # Django templates
│   ├── holidays/          # Discovery pages
│   ├── calendars/         # My Calendar
│   └── account/           # Login/signup
├── static/                # CSS, JS, images
├── docker-compose.yml     # Full stack definition
├── Dockerfile             # Python + Node container
└── requirements.txt       # Python dependencies
```



# Social Auth (optional)
GOOGLE_OAUTH_CLIENT_ID=
GOOGLE_OAUTH_CLIENT_SECRET=
```


## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- **Django** - The web framework for perfectionists
- **HTMX** - High power tools for HTML
- **Tailwind CSS** - Rapidly build modern websites
- **All holiday data providers** - Making this possible

## Contact

- **Website:** https://eld (coming soon)
- **Email:** coming soon ...
- **Twitter:** coming soon ...

# eld - Project Modifications & Edits Documentation

This document tracks all modifications and edits made to the eld (Every Little Day) project during quality assurance and completion.

**Last Updated**: November 28, 2025

> **See `.github/copilot-instructions.md` for complete architecture and technical patterns.**

---

## Summary of Changes

This project underwent comprehensive quality assurance focusing on:
- ✅ Fixing import errors preventing code execution
- ✅ Creating missing modules referenced in code
- ✅ Installing missing dependencies
- ✅ Establishing AI agent guidelines
- ✅ Code organization and documentation cleanup

---

## 1. Created `.github/copilot-instructions.md`

**Date**: November 28, 2025  
**Type**: New File  
**Status**: ✅ Complete

Comprehensive AI agent guide for developers working with the codebase. Contains detailed architecture, patterns, workflows, and common tasks.

**Why**: Centralizes project knowledge for faster AI agent onboarding and prevents reading multiple files to understand basic patterns.


## 2. Created `apps/holidays/services/deduplicator.py`

**Date**: November 28, 2025  
**Type**: New Module  
**Status**: ✅ Complete

Implements fuzzy matching deduplication logic for holidays from multiple sources. Handles name variations, date proximity for lunar holidays, and merges duplicate entries while preserving source attribution.

**Key Features**:
- Fuzzy name matching using difflib.SequenceMatcher (85% threshold)
- Date proximity matching for lunar-based holidays (±3 days)
- Source merging and smart category union
- Data completeness optimization

**Why**: Referenced in `apps/holidays/tasks.py` but was missing. Essential for handling duplicates from 10+ API sources and preventing data quality issues.


## 3. Fixed Django Signals Import in `apps/accounts/models.py`

**Date**: November 28, 2025  
**Type**: Bug Fix  
**Status**: ✅ Complete

**Change**: Updated import from `django.db.signals` to `django.db.models.signals` (Django 5.2 compatibility)

**Impact**: Enables automatic UserProfile and UserCalendar creation during user signup via Django signal handlers.


## 4. Installed `icalendar` Package

**Date**: November 28, 2025  
**Type**: Dependency  
**Status**: ✅ Complete

Used in `apps/calendars/utils.py` to generate .ics (iCalendar) files for calendar export to Google Calendar, Apple Calendar, and Outlook.

**Impact**: Enables one-click calendar sync via iCal feeds served at `/calendar/feed/{feed_token}/`

## 5. Installed `django-environ` Package

**Date**: November 28, 2025  
**Type**: Dependency  
**Status**: ✅ Complete

Used in `eld/settings.py` for secure environment variable management from `.env` file.

**Impact**: Prevents hardcoding sensitive data and enables environment-based configuration for Docker deployment.


## Summary

| Item | Type | Status | Impact |
|------|------|--------|--------|
| AI Agent Instructions | New File | ✅ | Developer productivity |
| Holiday Deduplicator | New Module | ✅ | Data quality |
| Django Signals | Fix | ✅ | User registration |
| icalendar | Install | ✅ | Calendar export |
| django-environ | Install | ✅ | Config management |
| .gitignore | New File | ✅ | Version control hygiene |

---

## Files Affected

- **Created**: `.github/copilot-instructions.md`, `apps/holidays/services/deduplicator.py`, `.gitignore`
- **Modified**: `apps/accounts/models.py` (line 3)
- **Dependencies Installed**: `icalendar`, `django-environ`
