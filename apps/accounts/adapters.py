from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import resolve_url


class FitForgeSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_login_redirect_url(self, request):
        """Redirect new social-login users to profile setup if profile is incomplete."""
        user = request.user
        if hasattr(user, 'profile') and not user.profile.is_complete():
            return resolve_url("profile_setup")
        return resolve_url("dashboard")
