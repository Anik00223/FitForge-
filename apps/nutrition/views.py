from collections import defaultdict

from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.nutrition.forms import MealLogForm
from apps.nutrition.models import MealLog
from core.decorators import login_required_custom


@login_required_custom
def meal_log_view(request):
    form = MealLogForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        meal = form.save(commit=False)
        meal.user = request.user
        meal.save()
        messages.success(request, "Meal logged.")
        return redirect("meal_log")
    today = timezone.localdate()
    meals = MealLog.objects.filter(user=request.user, date=today)
    grouped = defaultdict(list)
    for meal in meals:
        grouped[meal.get_meal_type_display()].append(meal)
    totals = meals.aggregate(
        calories=Sum("calories"),
        protein=Sum("protein_g"),
        carbs=Sum("carbs_g"),
        fats=Sum("fats_g"),
    )
    clean_totals = {key: value or 0 for key, value in totals.items()}
    diet_profile = request.user.diet_profile if hasattr(request.user, "diet_profile") else None
    calorie_progress = 0
    if diet_profile and diet_profile.daily_calories_target:
        calorie_progress = min(100, int((clean_totals["calories"] / diet_profile.daily_calories_target) * 100))
    return render(
        request,
        "nutrition/meal_log.html",
        {
            "form": form,
            "grouped_meals": dict(grouped),
            "totals": clean_totals,
            "diet_profile": diet_profile,
            "calorie_progress": calorie_progress,
        },
    )


@login_required_custom
def delete_meal(request, pk):
    meal = get_object_or_404(MealLog, pk=pk, user=request.user)
    if request.method == "POST":
        meal.delete()
        messages.success(request, "Meal removed.")
    return redirect("meal_log")
