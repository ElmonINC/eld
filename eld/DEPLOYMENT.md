# 🚀 Deployment Guide

This guide covers deploying **eld** to production on various platforms.

## Table of Contents
- [Railway Deployment](#railway-deployment)
- [Render Deployment](#render-deployment)
- [DigitalOcean Deployment](#digitalocean-deployment)
- [General Production Setup](#general-production-setup)

---

## Railway Deployment

[Railway](https://railway.app) is the easiest way to deploy eld.

### Steps:

1. **Fork this repository** on GitHub

2. **Sign up** at [railway.app](https://railway.app)

3. **Create a new project** → "Deploy from GitHub repo"

4. **Add services:**
   - PostgreSQL (from Railway marketplace)
   - Redis (from Railway marketplace)
   - Your Django app (from GitHub)

5. **Set environment variables** in Django service:
```bash
DEBUG=False
SECRET_KEY=<generate-strong-key>
ALLOWED_HOSTS=${{RAILWAY_PUBLIC_DOMAIN}}
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
CELERY_BROKER_URL=${{Redis.REDIS_URL}}
CELERY_RESULT_BACKEND=${{Redis.REDIS_URL}}
```

6. **Add start command:**
```bash
python manage.py migrate && python manage.py collectstatic --noinput && gunicorn eld.wsgi:application
```

7. **Add Celery worker** (new service):
   - Same repo
   - Start command: `celery -A eld worker --loglevel=info`

8. **Add Celery beat** (new service):
   - Same repo
   - Start command: `celery -A eld beat --loglevel=info`

9. **Seed data:**
```bash
railway run python manage.py seed_holidays
```

**✅ Done! Your app is live.**

---

## Render Deployment

[Render](https://render.com) offers great free tier options.

### Steps:

1. **Sign up** at [render.com](https://render.com)

2. **Create PostgreSQL database**
   - Name: `eld-db`
   - Plan: Free
   - Copy the Internal Database URL

3. **Create Redis instance**
   - Name: `eld-redis`
   - Plan: Free
   - Copy the Internal Redis URL

4. **Create Web Service**
   - Connect GitHub repo
   - Name: `eld`
   - Environment: Docker
   - Plan: Free or Starter

5. **Add environment variables:**
```bash
DEBUG=False
SECRET_KEY=<generate-strong-key>
DATABASE_URL=<postgres-internal-url>
REDIS_URL=<redis-internal-url>
CELERY_BROKER_URL=<redis-internal-url>
PYTHON_VERSION=3.12.0
```

6. **Build command:**
```bash
pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
```

7. **Start command:**
```bash
gunicorn eld.wsgi:application --bind 0.0.0.0:$PORT
```

8. **Create Background Worker** (for Celery):
   - Same repo
   - Start command: `celery -A eld worker --loglevel=info`

9. **Create Cron Job** (for Celery Beat):
   - Command: `python manage.py refresh_holidays`
   - Schedule: Daily at 2 AM

**✅ Deployed!**

---

## DigitalOcean Deployment

For full control, deploy on DigitalOcean with Docker.

### Prerequisites:
- DigitalOcean account
- Domain name (optional)

### Steps:

1. **Create Droplet**
   - Ubuntu 22.04 LTS
   - 2GB RAM minimum (for Redis + PostgreSQL)
   - Enable backups

2. **SSH into droplet:**
```bash
ssh root@your-droplet-ip
```

3. **Install Docker:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt install docker-compose -y
```

4. **Clone repository:**
```bash
git clone https://github.com/yourusername/eld.git
cd eld
```

5. **Create production .env:**
```bash
cp .env.example .env
nano .env
```

Update with production values:
```bash
DEBUG=False
SECRET_KEY=<strong-random-key>
ALLOWED_HOSTS=yourdomain.com,your-ip
DATABASE_URL=postgresql://eld_user:strong_password@db:5432/eld_db
```

6. **Update docker-compose.yml for production:**
```yaml
# Change web command to:
command: >
  sh -c "python manage.py migrate &&
         python manage.py collectstatic --noinput &&
         gunicorn eld.wsgi:application --bind 0.0.0.0:8000"
```

7. **Start services:**
```bash
docker-compose up -d --build
```

8. **Seed data:**
```bash
docker-compose exec web python manage.py seed_holidays
```

9. **Setup Nginx reverse proxy:**
```bash
apt install nginx -y
nano /etc/nginx/sites-available/eld
```

Add:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /root/eld/staticfiles/;
    }
}
```

Enable:
```bash
ln -s /etc/nginx/sites-available/eld /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

10. **Setup SSL with Let's Encrypt:**
```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d yourdomain.com
```

**✅ Production ready!**

---

## General Production Setup

### Security Checklist

✅ **Set DEBUG=False**
✅ **Use strong SECRET_KEY**
✅ **Configure ALLOWED_HOSTS properly**
✅ **Use environment variables for secrets**
✅ **Enable HTTPS (SSL certificate)**
✅ **Setup regular database backups**
✅ **Configure CORS if using API**
✅ **Enable Django security middleware**

### Performance Optimization

1. **Use gunicorn workers:**
```bash
gunicorn eld.wsgi:application --workers 4 --bind 0.0.0.0:8000
```

2. **Configure Redis caching:**
```python
# Already configured in settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
    }
}
```

3. **Setup CDN for static files** (optional):
   - Use AWS S3 + CloudFront
   - Or Cloudflare

4. **Monitor with Flower:**
   - Access at yourdomain.com:5555
   - Protect with authentication in production

### Monitoring

1. **Setup error tracking:**
   - Sentry
   - Rollbar

2. **Setup uptime monitoring:**
   - UptimeRobot
   - Pingdom

3. **Log management:**
   - Papertrail
   - Logtail

### Backup Strategy

1. **Database backups:**
```bash
# Daily automated backups
pg_dump eld_db > backup_$(date +%Y%m%d).sql
```

2. **Upload to cloud storage:**
   - AWS S3
   - Backblaze B2

### Environment Variables Reference

```bash
# Required
DEBUG=False
SECRET_KEY=<strong-random-key>
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0

# Email (for production)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Social Auth (optional)
GOOGLE_OAUTH_CLIENT_ID=your-google-id
GOOGLE_OAUTH_CLIENT_SECRET=your-google-secret
GITHUB_OAUTH_CLIENT_ID=your-github-id
GITHUB_OAUTH_CLIENT_SECRET=your-github-secret

# Holiday APIs (recommended)
CALENDARIFIC_API_KEY=your-api-key
ABSTRACT_API_KEY=your-api-key

# Site
SITE_URL=https://yourdomain.com
SITE_NAME=eld
```

---

## Troubleshooting

### Database connection errors
```bash
# Check database is running
docker-compose ps

# Check logs
docker-compose logs db
```

### Static files not loading
```bash
# Collect static files
python manage.py collectstatic --noinput

# Check STATIC_ROOT setting
```

### Celery not running tasks
```bash
# Check worker is running
docker-compose ps celery_worker

# Check logs
docker-compose logs celery_worker

# Manually test task
docker-compose exec web python manage.py shell
>>> from apps.holidays.tasks import refresh_all_holidays
>>> refresh_all_holidays.delay()
```

### Migration errors
```bash
# Reset migrations (DANGEROUS - only in dev)
python manage.py migrate --fake-initial

# Or create fresh migrations
rm apps/*/migrations/00*.py
python manage.py makemigrations
python manage.py migrate
```

---

## Support

For deployment issues:
- 📧 Email: support@eld.app
- 💬 GitHub Issues: https://github.com/yourusername/eld/issues
- 📖 Docs: https://docs.eld.app

**Happy deploying! 🚀**