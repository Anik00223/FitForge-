from datetime import timedelta

import redis
from django.utils import timezone


def check_redis(url: str) -> tuple[bool, str]:
    """Return ``(ok, detail)`` after pinging the Redis instance at ``url``.

    Used by the readiness probe and any other code that needs a quick
    canary check on the cache/broker without importing the full
    ``django_redis`` machinery.
    """
    client = redis.Redis.from_url(url, socket_connect_timeout=2, socket_timeout=2)
    try:
        if not client.ping():
            return False, "ping returned false"
        return True, "ok"
    finally:
        try:
            client.close()
        except Exception:  # pragma: no cover  - cleanup best-effort
            pass


def calculate_bmi(weight_kg: float, height_cm: float):
    if not weight_kg or not height_cm:
        return None
    height_m = height_cm / 100
    bmi = round(weight_kg / (height_m * height_m), 1)
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal Weight"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    return bmi, category


def calculate_tdee(weight_kg, height_cm, age, sex, activity_level):
    if sex == "M":
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "very": 1.725,
    }
    return int(bmr * multipliers.get(activity_level, 1.2))


def calculate_macros(tdee: int, goal: str) -> dict:
    ratios = {
        "lose": (0.30, 0.40, 0.30),
        "gain": (0.30, 0.50, 0.20),
        "maintain": (0.25, 0.50, 0.25),
        "endurance": (0.20, 0.60, 0.20),
    }
    protein_ratio, carb_ratio, fat_ratio = ratios.get(goal, ratios["maintain"])
    return {
        "protein_g": round((tdee * protein_ratio) / 4),
        "carbs_g": round((tdee * carb_ratio) / 4),
        "fats_g": round((tdee * fat_ratio) / 9),
    }


def get_bmi_badge_class(category: str) -> str:
    return {
        "Underweight": "badge-info",
        "Normal Weight": "badge-success",
        "Overweight": "badge-warning",
        "Obese": "badge-danger",
    }.get(category, "badge-secondary")


def get_workout_streak(user) -> int:
    from apps.tracker.models import WorkoutLog

    streak = 0
    day = timezone.localdate()
    while WorkoutLog.objects.filter(user=user, date=day).exists():
        streak += 1
        day -= timedelta(days=1)
    return streak
