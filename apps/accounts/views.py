from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render

from apps.accounts.forms import LoginForm, ProfileSetupForm, SignupForm
from apps.nutrition.models import DietProfile
from core.decorators import login_required_custom
from core.utils import calculate_macros, calculate_tdee


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(request, "Account created. Build your profile so FitForge can personalize your plan.")
        return redirect("profile_setup")
    return render(request, "accounts/signup.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = LoginForm(request.POST or None, request=request)
    if request.method == "POST" and form.is_valid():
        login(request, form.cleaned_data["user"], backend="django.contrib.auth.backends.ModelBackend")
        return redirect("dashboard")
    return render(request, "accounts/login.html", {"form": form})


from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from core.supabase_client import get_user_from_token
from core.supabase_auth import get_or_create_user

@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("home")


@login_required_custom
def profile_setup(request):
    profile = request.user.profile
    form = ProfileSetupForm(request.POST or None, instance=profile)
    targets = None
    if request.method == "POST" and form.is_valid():
        profile = form.save()
        tdee = calculate_tdee(
            profile.weight_kg,
            profile.height_cm,
            profile.age,
            profile.sex,
            profile.activity_level,
        )
        if profile.fitness_goal == "lose":
            calories = int(tdee * 0.85)
        elif profile.fitness_goal == "gain":
            calories = int(tdee * 1.10)
        else:
            calories = tdee
        macros = calculate_macros(calories, profile.fitness_goal)
        DietProfile.objects.update_or_create(
            user=request.user,
            defaults={
                "daily_calories_target": calories,
                "protein_g": macros["protein_g"],
                "carbs_g": macros["carbs_g"],
                "fats_g": macros["fats_g"],
            },
        )
        targets = {"calories": calories, **macros}
        messages.success(request, "Profile saved. Your plan targets are ready.")
        return redirect("planner")
    return render(request, "accounts/profile_setup.html", {"form": form, "targets": targets})


@csrf_exempt
@require_POST
def supabase_login(request):
    """Exchange a Supabase access token for a Django session.

    Expects JSON POST: {"access_token": "..."}
    Returns JSON success or an error code.
    """
    access_token = None
    try:
        payload = json.loads(request.body.decode() or "{}")
        access_token = payload.get("access_token")
    except Exception:
        access_token = request.POST.get("access_token")

    if not access_token:
        return JsonResponse({"error": "access_token required"}, status=400)

    sup_user = get_user_from_token(access_token, service_role=True)
    if not sup_user:
        return JsonResponse({"error": "invalid_token"}, status=401)

    user = get_or_create_user(sup_user)
    if not user:
        return JsonResponse({"error": "user_creation_failed"}, status=500)

    # Create a Django session for the user
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    return JsonResponse({"success": True})
