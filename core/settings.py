"""Settings shim: import environment-specific settings.

By default this module imports `core.settings.local`. Use the
`DJANGO_SETTINGS_ENV` environment variable to select `production`.
"""

import os

env = os.environ.get('DJANGO_SETTINGS_ENV', 'local')
if env == 'production':
    from .settings.production import *  # noqa: F401,F403
else:
    from .settings.local import *  # noqa: F401,F403
