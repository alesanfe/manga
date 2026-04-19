# Development Guide

This guide covers development practices, workflows, and conventions for the Manga Downloader project.

## Table of Contents

- [Environment Setup](#environment-setup)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Testing](#testing)
- [Database Management](#database-management)
- [Adding New Features](#adding-new-features)
- [Debugging](#debugging)

## Environment Setup

### Prerequisites

- Python 3.8+
- Chrome/Chromium + ChromeDriver (for Selenium)
- Git

### Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/alesanfe/manga.git
   cd manga
   ```

2. **Create and activate a virtual environment:**
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Configure environment variables:**
   ```powershell
   copy config\env.sample .env
   # Edit .env with your values
   ```

5. **Apply database migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Load initial data (optional):**
   ```bash
   python utils/db_populate.py
   ```

7. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

8. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

The application will be available at http://127.0.0.1:8000

### Windows Quick Setup

Use the provided PowerShell script for automated setup:

```powershell
.\scripts\setup_dev.ps1
```

Add `-Populate` flag to load initial data:

```powershell
.\scripts\setup_dev.ps1 -Populate
```

## Development Workflow

### Branch Strategy

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: Feature branches
- `bugfix/*`: Bug fix branches

### Creating a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### Commit Conventions

Use clear, descriptive commit messages:

```
feat: add manga download API endpoint
fix: resolve PDF generation issue for large chapters
docs: update README with new setup instructions
refactor: simplify manga_services.py
test: add tests for authentication views
```

### Pre-commit Hooks

The project uses pre-commit hooks for code quality:

- **black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **trailing-whitespace**: Remove trailing whitespace
- **end-of-file-fixer**: Ensure files end with newline

Hooks run automatically before commits. To skip (not recommended):

```bash
git commit --no-verify -m "Your message"
```

## Code Style

### Python

Follow PEP 8 with these tools:

- **black**: Auto-formatting (line length 88)
- **isort**: Import organization
- **flake8**: Linting

Format code manually:

```bash
black .
isort .
flake8 .
```

### Django Conventions

- Use class-based views for complex logic
- Keep business logic in `utils/` or service classes
- Use Django REST Framework for API endpoints
- Follow Django's naming conventions:
  - Models: `PascalCase`
  - Functions/variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`

### File Organization

- **apps/**: Django applications (MVC pattern)
- **utils/**: Reusable business logic
- **static/**: Static files organized by type
- **templates/**: HTML templates organized by app

## Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.manga

# Run specific test
python manage.py test apps.manga.tests.TestMangaDownload
```

### Writing Tests

Place tests in `tests.py` within each app:

```python
from django.test import TestCase

class MangaDownloadTest(TestCase):
    def setUp(self):
        # Setup test data
        pass

    def test_download_single_chapter(self):
        # Test implementation
        self.assertEqual(response.status_code, 200)
```

## Database Management

### Migrations

```bash
# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Rollback last migration
python manage.py migrate app_name migration_name
```

### Database Seeding

```bash
# Populate database with initial data
python utils/db_populate.py

# Load from JSON fixture
python manage.py loaddata data/initial_data.json
```

### Creating Search Index

```bash
# Create Whoosh search index
python utils/index_creator.py
```

## Adding New Features

### Adding a New Django App

1. Create the app:
   ```bash
   python manage.py startapp new_app apps/new_app
   ```

2. Add to `INSTALLED_APPS` in `core/settings/base.py`:
   ```python
   INSTALLED_APPS = [
       # ...
       'apps.new_app',
   ]
   ```

3. Configure URLs in `apps/new_app/urls.py` and include in `core/urls.py`

### Adding API Endpoints

1. Create serializers in `apps/your_app/serializer.py`
2. Add views in `apps/your_app/api.py` or `views.py`
3. Configure URLs in `apps/your_app/urls.py`

Example:

```python
# serializer.py
from rest_framework import serializers
from .models import YourModel

class YourModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = YourModel
        fields = '__all__'

# api.py
from rest_framework import viewsets
from .models import YourModel
from .serializer import YourModelSerializer

class YourModelViewSet(viewsets.ModelViewSet):
    queryset = YourModel.objects.all()
    serializer_class = YourModelSerializer
```

### Adding Utility Functions

Place reusable business logic in `utils/`:

```python
# utils/your_service.py
def your_function(param):
    """Documentation"""
    # Implementation
    return result
```

## Debugging

### Django Debug Toolbar

Install and configure for local development:

```bash
pip install django-debug-toolbar
```

Add to `INSTALLED_APPS` in `core/settings/local.py`:

```python
INSTALLED_APPS += ['debug_toolbar']
```

### Logging

Configure logging in `core/settings/local.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

### Common Issues

**ImportError: No module named 'apps'**
- Ensure you're running from project root
- Check `PYTHONPATH` includes project directory

**Database connection errors**
- Verify `.env` configuration
- Check database server is running
- Ensure migrations are applied

**Static files not loading**
- Run `python manage.py collectstatic`
- Check `STATIC_ROOT` and `STATICFILES_DIRS` in settings

## Security Best Practices

- Never commit `.env` or secrets
- Use `DEBUG=False` in production
- Keep dependencies updated:
  ```bash
  pip install --upgrade pip
  pip install -r requirements.txt --upgrade
  ```
- Scan for vulnerabilities:
  ```bash
  safety check --full-report
  ```
- Scan for secrets:
  ```bash
  detect-secrets scan > .secrets.baseline
  ```

## Useful Commands

```bash
# Django shell
python manage.py shell

# Create superuser
python manage.py createsuperuser

# Clear static files
python manage.py collectstatic --clear

# Check for issues
python manage.py check

# Format code
make lint  # or manually: black . && isort . && flake8 .
```

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Black Code Formatter](https://black.readthedocs.io/)
- [Pre-commit](https://pre-commit.com/)
