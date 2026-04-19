"""Production settings. Import from base and apply production-safe overrides.
"""

from .base import *  # noqa: F401,F403

# Production overrides
DEBUG = env.bool('DEBUG', default=False)

# Ensure SECRET_KEY is provided explicitly in production via DJANGO_SECRET_KEY
if 'changeme' in SECRET_KEY or SECRET_KEY == 'S#perS3crEt_007':
    raise RuntimeError('Set DJANGO_SECRET_KEY in production environment!')

# Security settings
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'

