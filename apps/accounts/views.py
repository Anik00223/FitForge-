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
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.cleaned_data["user"], backend="django.contrib.auth.backends.ModelBackend")
        return redirect("dashboard")
    return render(request, "accounts/login.html", {"form": form})


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
