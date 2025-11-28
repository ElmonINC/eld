# 🎉 eld - Every Little Day

**The world's most beautiful, complete, and joyful public holiday discovery + personal calendar app.**

Discover public holidays, religious observances, UN international days, and fun celebrations from 195+ countries. One click adds them to your personal calendar. Export to Google Calendar, Apple Calendar, or download as .ics.

![eld Hero](https://via.placeholder.com/1200x600/8B5CF6/FFFFFF?text=eld+-+Every+Celebration+Matters)

## ✨ Features

### 🌍 **Master Holiday Database**
- **10+ Global Sources** merged daily via Celery:
  - Nager.Date API (195+ countries)
  - Calendarific API
  - AbstractAPI Holidays
  - UN Observances
  - TimeAndDate.com
  - Checkiday.com
  - Wikipedia public holidays
  - National Day Calendar
  - Days of the Year
  - Google public holiday calendars

- **Smart Deduplication** - Fuzzy matching prevents duplicates
- **Rich Metadata** - Country flags, categories, descriptions, lunar dates
- **Auto-refresh** - Daily Celery Beat job updates everything

### 🔍 **Gorgeous Discovery Experience**
Three beautiful views (zero page reloads, pure HTMX):
- **📅 Next 7 Days** - Hero layout with live countdowns
- **📆 This Month** - Calendar + list hybrid
- **🗓️ Full Year** - Expandable 12-month grid

**Instant Filters:**
- Country/Region (with flag picker)
- Type (Public | Religious | International | Fun/Quirky | Seasonal)
- Search with autocomplete

### ⚡ **One-Click "Add to My Calendar"**
- Login required (beautiful social + email auth)
- Single click → confetti animation → saved
- Bulk select mode
- Reminder options (none / 1 day / morning of)

### 📲 **Personal Calendar & Export**
The killer feature:
- **Private iCal feed** (webcal:// compatible)
- **One-click sync** to Google, Apple, Outlook
- **Download .ics** anytime
- Works perfectly with every major calendar app

### 🎨 **UI/UX Perfection**
- Mobile-first responsive design
- Dark & light mode (auto + manual toggle)
- Tailwind-powered celebration theme
- Confetti animations for fun holidays
- Loading skeletons, smooth transitions
- Toast notifications

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- That's it! Everything else is containerized.

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/eld.git
cd eld
```

2. **Copy environment file:**
```bash
cp .env.example .env
```

3. **Start everything with one command:**
```bash
docker-compose up --build
```

4. **In a new terminal, run migrations and seed data:**
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py seed_holidays
```

5. **Create a superuser:**
```bash
docker-compose exec web python manage.py createsuperuser
```

6. **Visit the app:**
- **App:** http://localhost:8000
- **Admin:** http://localhost:8000/admin
- **Flower (Celery monitoring):** http://localhost:5555

## 📚 Tech Stack

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

## 📖 Usage Guide

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

## 🛠️ Management Commands

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

## 🎨 Design Philosophy

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

## 📁 Project Structure

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

## 🔧 Configuration

### Environment Variables

Key variables in `.env`:

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:pass@db:5432/eld_db

# Redis & Celery
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0

# Holiday APIs (optional but recommended)
NAGER_API_KEY=
CALENDARIFIC_API_KEY=
ABSTRACT_API_KEY=

# Social Auth (optional)
GOOGLE_OAUTH_CLIENT_ID=
GOOGLE_OAUTH_CLIENT_SECRET=
```

### Getting API Keys

**Free tiers available:**

1. **Calendarific** - https://calendarific.com/api-documentation
2. **AbstractAPI** - https://app.abstractapi.com/api/holidays/tester
3. **Nager.Date** - No key required! https://date.nager.at

## 🚀 Deployment

### Production Checklist

1. **Set environment:**
```bash
DEBUG=False
SECRET_KEY=<strong-random-key>
ALLOWED_HOSTS=yourdomain.com
```

2. **Use gunicorn:**
```bash
gunicorn eld.wsgi:application --bind 0.0.0.0:8000
```

3. **Run migrations:**
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

4. **Start Celery:**
```bash
celery -A eld worker --loglevel=info
celery -A eld beat --loglevel=info
```

5. **Setup HTTPS** - Use Let's Encrypt + Nginx

### Recommended Services
- **Hosting:** Railway, Render, DigitalOcean
- **Database:** Managed PostgreSQL
- **Redis:** Managed Redis (Redis Cloud, Upstash)
- **Domain:** Any registrar

## 🤝 Contributing

We welcome contributions! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

**Areas we'd love help with:**
- More holiday data sources
- Translations (i18n)
- Mobile apps (React Native)
- Performance optimizations

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- **Django** - The web framework for perfectionists
- **HTMX** - High power tools for HTML
- **Tailwind CSS** - Rapidly build modern websites
- **All holiday data providers** - Making this possible

## 📧 Contact

- **Website:** https://eld.app (coming soon)
- **Email:** coming soon ...
- **Twitter:** coming soon ...

---

**Made with ❤️ for celebration lovers worldwide**

🎉 *Every day is a reason to celebrate* 🌍