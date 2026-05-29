from django.conf import settings


def global_context(request):
    return {
        "app_name": "FitForge",
        "tagline": "Your Fitness. Your Victory.",
        "SUPABASE_URL": getattr(settings, "SUPABASE_URL", ""),
        "SUPABASE_PUBLISHABLE_KEY": getattr(settings, "SUPABASE_PUBLISHABLE_KEY", ""),
    }
