from collections import defaultdict

from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.nutrition.models import MealLog
from apps.tracker.forms import BMILogForm, WorkoutLogForm
from apps.tracker.models import BMILog, WorkoutLog
from core.decorators import login_required_custom
from core.utils import calculate_bmi, get_bmi_badge_class, get_workout_streak


def home_view(request):
    return render(request, "home.html")


@login_required_custom
def dashboard_view(request):
    profile = getattr(request.user, "profile", None)
    if not profile or not profile.is_complete():
        messages.warning(request, "Complete your profile before opening the dashboard.")
        return redirect("profile_setup")
    today = timezone.localdate()
    latest_bmi = request.user.bmi_logs.first()
    calories_today = (
        MealLog.objects.filter(user=request.user, date=today).aggregate(total=Sum("calories"))["total"] or 0
    )
    meals_today = MealLog.objects.filter(user=request.user, date=today)
    meal_totals = meals_today.aggregate(
        protein=Sum("protein_g"),
        carbs=Sum("carbs_g"),
        fats=Sum("fats_g"),
    )
    bmi_logs = list(BMILog.objects.filter(user=request.user).order_by("date")[:30])
    recent_workouts = WorkoutLog.objects.filter(user=request.user)[:5]
    context = {
        "profile": profile,
        "latest_bmi": latest_bmi,
        "bmi_badge": get_bmi_badge_class(latest_bmi.category) if latest_bmi else "badge-info",
        "total_workouts": WorkoutLog.objects.filter(user=request.user).count(),
        "calories_today": calories_today,
        "streak": get_workout_streak(request.user),
        "recent_workouts": recent_workouts,
        "bmi_labels": [log.date.strftime("%d %b") for log in bmi_logs],
        "bmi_values": [log.bmi for log in bmi_logs],
        "meal_totals": meal_totals,
        "diet_profile": getattr(request.user, "diet_profile", None),
    }
    return render(request, "tracker/dashboard.html", context)


@login_required_custom
def bmi_add_view(request):
    form = BMILogForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        bmi, category = calculate_bmi(form.cleaned_data["weight_kg"], form.cleaned_data["height_cm"])
        log = form.save(commit=False)
        log.user = request.user
        log.bmi = bmi
        log.category = category
        log.save()
        profile = request.user.profile
        profile.weight_kg = log.weight_kg
        profile.height_cm = log.height_cm
        profile.save(update_fields=["weight_kg", "height_cm", "updated_at"])
        messages.success(request, f"BMI logged: {bmi} ({category}).")
        return redirect("bmi_history")
    return render(request, "tracker/bmi_add.html", {"form": form})


@login_required_custom
def bmi_history_view(request):
    logs = BMILog.objects.filter(user=request.user)
    chart_logs = list(logs.order_by("date"))
    return render(
        request,
        "tracker/bmi_history.html",
        {
            "logs": logs,
            "labels": [log.date.strftime("%d %b") for log in chart_logs],
            "values": [log.bmi for log in chart_logs],
            "badge_for": get_bmi_badge_class,
        },
    )


@login_required_custom
def workout_add_view(request):
    form = WorkoutLogForm()
    if request.method == "POST":
        exercises = request.POST.getlist("exercise")
        sets = request.POST.getlist("sets")
        reps = request.POST.getlist("reps")
        weights = request.POST.getlist("weight_kg")
        notes = request.POST.getlist("notes")
        created = 0
        for index, exercise in enumerate(exercises):
            if not exercise.strip():
                continue
            WorkoutLog.objects.create(
                user=request.user,
                exercise=exercise.strip(),
                sets=int(sets[index] or 1),
                reps=int(reps[index] or 1),
                weight_kg=float(weights[index]) if weights[index] else None,
                notes=notes[index].strip() if index < len(notes) else "",
            )
            created += 1
        if created:
            messages.success(request, f"Logged {created} workout exercise{'s' if created != 1 else ''}.")
            return redirect("workout_history")
        messages.error(request, "Add at least one exercise.")
    return render(request, "tracker/workout_add.html", {"form": form})


@login_required_custom
def workout_history_view(request):
    logs = WorkoutLog.objects.filter(user=request.user)
    grouped = defaultdict(list)
    for log in logs:
        grouped[log.date].append(log)
    return render(request, "tracker/workout_history.html", {"grouped_logs": dict(grouped)})


@login_required_custom
def workout_delete_view(request, pk):
    workout = get_object_or_404(WorkoutLog, pk=pk, user=request.user)
    if request.method == "POST":
        workout.delete()
        messages.success(request, "Workout exercise deleted.")
    return redirect("workout_history")
