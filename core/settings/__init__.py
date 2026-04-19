# Settings package
import os

# Determine which settings module to use based on environment
# Default to 'local' for development, can be overridden with DJANGO_ENV
environment = os.environ.get('DJANGO_ENV', os.environ.get('ENV', 'local')).lower()

if environment == 'production':
    from .production import *  # noqa: F401,F403
elif environment == 'base':
    from .base import *  # noqa: F401,F403
else:
    # Default to local settings for development
    from .local import *  # noqa: F401,F403
