# Project Structure

```
manga/
|
# Core Django files
|-- manage.py                    # Django management script
|-- core/                        # Core Django configuration
|   |-- settings.py              # Settings shim (imports local/production)
|   |-- settings/                # Environment-specific settings
|   |   |-- base.py              # Base settings
|   |   |-- local.py             # Local development settings
|   |   |-- production.py        # Production settings
|   |-- asgi.py                  # ASGI configuration
|   |-- urls.py                  # Main URL routing
|   |-- wsgi.py                  # WSGI configuration
|   |-- staticfiles/             # Core static files
|
# Django applications
|-- apps/                        # Django apps
|   |-- __init__.py              # Apps package initialization
|   |-- config.py                # General apps configuration
|   |-- context_processors.py    # Global context processors
|   |-- authentication/          # User authentication
|   |   |-- __init__.py
|   |   |-- admin.py
|   |   |-- config.py
|   |   |-- forms.py             # Authentication forms
|   |   |-- models.py
|   |   |-- tests.py
|   |   |-- urls.py              # Authentication routes
|   |   |-- views.py             # Authentication views
|   |   |-- migrations/          # Database migrations
|   |-- home/                    # Main app
|   |   |-- __init__.py
|   |   |-- admin.py
|   |   |-- config.py
|   |   |-- models.py
|   |   |-- tests.py
|   |   |-- urls.py              # Main routes
|   |   |-- views.py             # Main views
|   |   |-- migrations/          # Database migrations
|   |-- manga/                   # Manga functionality
|   |   |-- admin.py
|   |   |-- api.py               # REST API for downloads
|   |   |-- config.py
|   |   |-- models.py            # Data models (Manga, Author, Genre, Score)
|   |   |-- serializer.py        # DRF serializers
|   |   |-- tests.py
|   |   |-- urls.py              # Manga routes
|   |   |-- views.py             # Manga views
|   |   |-- migrations/          # Database migrations
|   |-- static/                  # App-specific static files
|
# Utilities
|-- utils/                       # Scripts and utilities
|   |-- __init__.py
|   |-- manga_services.py        # Manga download services
|   |-- db_populate.py           # Database population script
|   |-- index_creator.py         # Search index creation script
|
# Static files
|-- static/                      # Static files (CSS, JS, images)
|   |-- assets/                  # Black Dashboard theme assets
|   |   |-- css/                 # Stylesheets
|   |   |-- js/                  # JavaScript files
|   |   |   |-- core/            # Core JavaScript
|   |   |   |-- plugins/         # Third-party plugins
|   |   |-- scss/                # SCSS source files
|   |   |   |-- black-dashboard/ # Theme SCSS
|   |   |-- fonts/               # Font files
|   |   |-- img/                 # Images
|   |   |-- demo/                # Demo assets
|
# Templates
|-- templates/                   # HTML templates
|   |-- includes/                # Reusable components
|   |-- layouts/                 # Base layouts
|   |-- accounts/                # Authentication templates
|   |-- home/                    # Main templates
|   |-- manga/                   # Manga templates
|   |   |-- downloaders/         # Downloader-specific templates
|
# Configuration files
|-- docker/                      # Docker configuration directory
|   |-- Dockerfile              # Docker image definition
|   |-- gunicorn-cfg.py         # Gunicorn configuration
|   |-- base/                   # Base Docker compose configuration
|   |   |-- docker-compose.yml
|   |   |-- .env
|   |-- dev/                    # Development Docker compose configuration
|   |   |-- docker-compose.yml
|   |   |-- .env
|   |-- prod/                   # Production Docker compose configuration
|   |   |-- docker-compose.yml
|   |   |-- .env
|   |-- nginx/                  # Nginx configuration
|   |   |-- manga-app.conf
|   |-- envs/                   # Environment variable templates
|   |   |-- .env.dev.example
|   |   |-- .env.prod.example
|
# Scripts
|-- scripts/                     # System scripts
|   |-- entrypoint.sh           # Docker entrypoint
|   |-- setup_dev.ps1           # Windows development setup script
|
# Data files
|-- data/                        # Data storage
|   |-- initial_data.json       # Initial database data
|   |-- populate.json           # Population data
|
# Documentation
|-- docs/                        # Documentation
|   |-- CHANGELOG.md            # Version history
|   |-- LICENSE.md              # License
|   |-- PROJECT_STRUCTURE.md   # This file
|
|
# Dependencies
|-- requirements.txt             # Python dependencies
|-- requirements-dev.txt         # Development dependencies
|
# Environment
|-- .env                         # Environment variables (not in git)
|-- .gitignore                  # Git ignore rules
|-- .pre-commit-config.yaml     # Pre-commit hooks configuration
|-- .secrets.baseline           # Secrets scanning baseline
|
# Build/CI files
|-- Makefile                     # Make commands for development
|
# Static files (generated)
|-- staticfiles/                 # Collected static files (don't edit manually)
```

## Directory Purposes

- **core/**: Django core configuration and settings with environment-specific modules
- **apps/**: Django applications following MVC pattern (authentication, home, manga)
- **utils/**: Business logic services and utility scripts separated from apps
- **static/**: Static files at project root (CSS, JS, images, SCSS)
- **templates/**: HTML templates at project root organized by app
- **docker/**: Docker configuration files including Dockerfile, docker-compose files for different environments, nginx config, and gunicorn config
- **scripts/**: System initialization and deployment scripts
- **data/**: Database seed files and data dumps
- **docs/**: Documentation and project information
- **staticfiles/**: Generated static files (don't edit manually)

## Settings Structure

The project uses a modular settings structure:

- **core/settings.py**: Shim that imports environment-specific settings
- **core/settings/base.py**: Base settings shared across all environments
- **core/settings/local.py**: Local development settings (default)
- **core/settings/production.py**: Production settings (selected via DJANGO_SETTINGS_ENV)

Set `DJANGO_SETTINGS_ENV=production` to use production settings.
