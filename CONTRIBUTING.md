# 🤝 Contributing to eld

Thank you for considering contributing to **eld**! We welcome contributions from everyone.

## Getting Started

For initial setup and quick start instructions, see **[README.md](README.md)**.

This guide covers development conventions, code style, and contribution workflow.

## Development Conventions

We follow these conventions:

### Python (PEP 8)
- Use 4 spaces for indentation
- Line length: 100 characters max
- Use descriptive variable names
- Add docstrings to functions and classes

Example:
```python
def fetch_holidays(country_code: str, year: int) -> List[Dict]:
    """
    Fetch holidays for a specific country and year.
    
    Args:
        country_code: ISO 2-letter country code (e.g., 'US')
        year: Four-digit year (e.g., 2025)
    
    Returns:
        List of holiday dictionaries
    """
    # Implementation
    pass
```

### Django Best Practices
- Use class-based views when appropriate
- Keep views thin, business logic in services/
- Use Django ORM efficiently (select_related, prefetch_related)
- Add database indexes for frequently queried fields

### Templates & Frontend
- Use semantic HTML
- Tailwind utility classes for styling
- HTMX for interactivity (avoid custom JavaScript)
- Keep templates DRY with includes and extends

### Git Commits
Format: `type(scope): message`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

Examples:
```
feat(holidays): add support for Islamic calendar
fix(calendar): correct iCal feed timezone handling
docs(readme): update deployment instructions
```

## Areas to Contribute

### 🌍 Holiday Data Sources
Add new holiday data providers in `apps/holidays/services/holiday_fetcher.py`:

```python
def fetch_new_source(self, year: int) -> List[Dict]:
    """Fetch from NewSource API"""
    holidays = []
    # Implementation
    return holidays
```

### 🎨 UI/UX Improvements
- New views (timeline, map, etc.)
- Better mobile experience
- Accessibility enhancements
- Dark mode refinements

### 🌐 Internationalization
Help translate eld to other languages:

1. Create translation files:
```bash
python manage.py makemessages -l es  # Spanish
python manage.py makemessages -l fr  # French
```

2. Edit `.po` files in `locale/`

3. Compile:
```bash
python manage.py compilemessages
```

### 🧪 Testing
Add tests in `apps/*/tests.py`:

```python
from django.test import TestCase
from eld.apps.holidays.models import Holiday

class HolidayTestCase(TestCase):
    def test_holiday_creation(self):
        holiday = Holiday.objects.create(
            name="Test Day",
            date="2025-01-01"
        )
        self.assertEqual(holiday.year, 2025)
```

Run tests:
```bash
docker-compose exec web python manage.py test
```

### 📊 Performance
- Add caching where appropriate
- Optimize database queries
- Improve Celery task efficiency
- Add monitoring/metrics

## Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new features
3. **Run tests** to ensure nothing breaks
4. **Update CHANGELOG.md** with your changes
5. **Submit PR** with clear description

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added new tests

## Screenshots (if applicable)
[Add screenshots]

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
```

## Development Tips

### Working with Celery
Test tasks manually:
```bash
docker-compose exec web python manage.py shell
>>> from apps.holidays.tasks import refresh_all_holidays
>>> result = refresh_all_holidays()
>>> print(result)
```

### Database Management
```bash
# Create migration
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate

# Shell
docker-compose exec web python manage.py shell

# Database shell
docker-compose exec web python manage.py dbshell
```

### Debugging
```bash
# View logs
docker-compose logs -f web

# Django shell
docker-compose exec web python manage.py shell

# Access container
docker-compose exec web bash
```

### Working with Static Files
```bash
# Rebuild Tailwind CSS
docker-compose exec web npm run build:css

# Watch for changes
docker-compose exec web npm run watch:css

# Collect static files
docker-compose exec web python manage.py collectstatic
```

## Common Issues

### Port already in use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Database connection refused
```bash
# Restart database
docker-compose restart db

# Check if running
docker-compose ps
```

### Migrations conflict
```bash
# Roll back migration
docker-compose exec web python manage.py migrate app_name migration_name

# Delete conflicting migration files
# Then remake migrations
docker-compose exec web python manage.py makemigrations
```

## Code Review Guidelines

When reviewing PRs, check for:
- ✅ Code quality and readability
- ✅ Test coverage
- ✅ Documentation updates
- ✅ No security vulnerabilities
- ✅ Performance considerations
- ✅ Mobile responsiveness
- ✅ Accessibility

## Recognition

Contributors will be:
- 🌟 Listed in README.md
- 🎉 Mentioned in release notes
- 💝 Given our eternal gratitude

## Questions?

- 💬 **GitHub Discussions**: Ask questions and share ideas
- 📧 **Email**: dev@eld.app
- 🐛 **Issues**: Report bugs or request features

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for making eld better! 🎉**