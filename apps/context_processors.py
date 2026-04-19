from django.conf import settings

def cfg_assets_root(request):
    return { 'ASSETS_ROOT' : settings.ASSETS_ROOT }

def user_profile(request):
    if request.user.is_authenticated:
        from apps.authentication.models import UserProfile
        try:
            profile = UserProfile.objects.get(user=request.user)
            return {'user_profile': profile}
        except UserProfile.DoesNotExist:
            return {'user_profile': None}
    return {'user_profile': None}

