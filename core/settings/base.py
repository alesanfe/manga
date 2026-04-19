# -*- encoding: utf-8 -*-
"""
Base settings for the project. This file is imported by local/production settings.
"""

import os
import uuid

import environ
# Use pymysql as a drop-in replacement for mysqlclient (Windows compatibility)
import pymysql

pymysql.install_as_MySQLdb()

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, True)
)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CORE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Take environment variables from .env file
environ.Env.read_env(os.path.join(CORE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
# Support DJANGO_SECRET_KEY (preferred) and fall back to legacy SECRET_KEY
SECRET_KEY = env('DJANGO_SECRET_KEY', default=env('SECRET_KEY', default='S#perS3crEt_007'))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

# Assets Management
ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets')

# Custom paths
WHOOSH_INDEX_PATH = '/tmp/whoosh_index'
DOWNLOAD_OUTPUT_PATH = os.path.join(BASE_DIR, 'manga_download.zip')

# Allow ALLOWED_HOSTS to be provided as a comma-separated list in env
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])
# CSRF trusted origins: construct from ALLOWED_HOSTS and SERVER if present
server_host = env('SERVER', default=None)
CSRF_TRUSTED_ORIGINS = []
for h in ALLOWED_HOSTS:
    if isinstance(h, str) and h.startswith('http'):
        CSRF_TRUSTED_ORIGINS.append(h)
    else:
        CSRF_TRUSTED_ORIGINS.append('http://' + h)
        CSRF_TRUSTED_ORIGINS.append('https://' + h)
if server_host:
    CSRF_TRUSTED_ORIGINS.append('https://' + server_host)

# Application definition

INSTALLED_APPS = [
    'material',
    'material.admin',
    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.home',  # Enable the inner home (home)
    'apps.manga',
    'apps.authentication'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'
LOGIN_REDIRECT_URL = "home"  # Route defined in home/urls.py
LOGOUT_REDIRECT_URL = "home"  # Route defined in home/urls.py
TEMPLATE_DIR = os.path.join(CORE_DIR, "templates")  # ROOT dir for templates

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.context_processors.cfg_assets_root',
                'apps.context_processors.user_profile',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

# Database configuration
# Prefer DATABASE_URL (12-factor), else fall back to DB_ENGINE + DB_* variables
database_url = env('DATABASE_URL', default=None)
if database_url:
    DATABASES = {
        'default': env.db('DATABASE_URL')
    }
elif env('DB_ENGINE', default='sqlite') == "mysql":
    DATABASES = {
        'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DB_NAME', default='manga_db'),
        'USER': env('DB_USERNAME', default='manga_db_usr'),
        'PASSWORD': env('DB_PASS', default='pass'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default=3306),
        },
    }
elif env('DB_ENGINE', default='sqlite') == "postgres":
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DB_NAME', default='manga_db'),
            'USER': env('DB_USERNAME', default='manga_db_usr'),
            'PASSWORD': env('DB_PASS', default='pass'),
            'HOST': env('DB_HOST', default='localhost'),
            'PORT': env('DB_PORT', default=5432),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': env('DB_NAME', default='db.sqlite3'),
        }
    }

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

#############################################################
# SRC: https://devcenter.heroku.com/articles/django-assets

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(CORE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(CORE_DIR, 'static'),
)

# Media files (User uploads)
MEDIA_ROOT = os.path.join(CORE_DIR, 'media')
MEDIA_URL = '/media/'

# Whitenoise configuration
if not DEBUG:
    # In production, use Whitenoise for all static files
    WHITENOISE_STATIC_ONLY = False
    WHITENOISE_USE_FINDERS = True
else:
    # In development, disable Whitenoise to use Django's static file serving
    WHITENOISE_USE_FINDERS = False
    WHITENOISE_AUTOREFRESH = False


#############################################################

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
DEFAULT_AUTO_FIELD_ADDITIONAL_OPTIONS = {
    'default': uuid.uuid4,
    'editable': False,
    'unique': True,
}

#############################################################

