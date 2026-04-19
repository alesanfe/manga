import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from apps.authentication.models import UserProfile

# Update admin profile to use the fixed image
admin = User.objects.get(username='admin')
profile = admin.profile
profile.profile_picture = 'profile_pictures/Captura_de_pantalla_2024-07-03_171239_fixed.png'
profile.save()
print(f"Updated admin profile to use: {profile.profile_picture}")

# Verify the update
profile.refresh_from_db()
print(f"Verified: {profile.profile_picture}")
