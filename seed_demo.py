import os
import django
from datetime import datetime, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.contrib.auth.models import User
from apps.accounts.models import UserProfile
from apps.nutrition.models import DietProfile, MealLog
from apps.tracker.models import BMILog, WorkoutLog

def seed():
    print("Clearing old demo data...")
    User.objects.filter(email="demo@fitforge.app").delete()

    print("Creating Demo User...")
    user = User.objects.create_user(
        username="demo@fitforge.app",
        email="demo@fitforge.app",
        password="FitForge123!",
        first_name="Alex",
        last_name="Forge"
    )

    print("Setting up User Profile...")
    profile = user.profile
    profile.age = 28
    profile.sex = "M"
    profile.weight_kg = 82.5
    profile.height_cm = 180
    profile.activity_level = "moderate"
    profile.fitness_goal = "gain"
    profile.dietary_preference = "high_protein"
    profile.save()

    print("Setting up Diet Profile...")
    diet = user.diet_profile
    diet.daily_calories_target = 2800
    diet.protein_g = 180
    diet.carbs_g = 300
    diet.fats_g = 80
    diet.save()

    print("Generating BMI History...")
    base_date = datetime.now().date() - timedelta(days=30)
    weights = [85.0, 84.2, 83.5, 83.0, 82.5]
    for i, w in enumerate(weights):
        bmi = round(w / ((180/100)**2), 1)
        cat = "Overweight" if bmi >= 25 else "Normal Weight"
        BMILog.objects.create(
            user=user,
            weight_kg=w,
            height_cm=180,
            bmi=bmi,
            category=cat,
            date=base_date + timedelta(days=i*7)
        )

    print("Generating Workout Logs...")
    workouts = [
        ("Barbell Squat", 4, 8, 100),
        ("Bench Press", 4, 8, 80),
        ("Deadlift", 3, 5, 120),
        ("Overhead Press", 3, 10, 50),
        ("Pull-ups", 3, 10, 0),
        ("Barbell Row", 4, 10, 70),
        ("Dumbbell Curls", 3, 12, 15),
        ("Tricep Pushdowns", 3, 15, 25),
        ("Leg Press", 4, 12, 200),
        ("Calf Raises", 4, 15, 60),
    ]
    
    for i, w in enumerate(workouts):
        WorkoutLog.objects.create(
            user=user,
            exercise=w[0],
            sets=w[1],
            reps=w[2],
            weight_kg=w[3],
            notes="Felt good, solid form." if i % 2 == 0 else "",
            date=datetime.now().date() - timedelta(days=(10-i))
        )

    print("Generating Meal Logs...")
    meals = [
        ("breakfast", "Oats with Whey Protein and Berries", 450, 35, 55, 10),
        ("lunch", "Chicken Breast with Rice and Broccoli", 600, 55, 65, 12),
        ("snack", "Greek Yogurt with Almonds", 250, 20, 15, 12),
        ("dinner", "Salmon with Sweet Potato and Asparagus", 550, 45, 45, 22),
        ("snack", "Casein Shake", 150, 25, 5, 2),
    ]
    
    for m in meals:
        MealLog.objects.create(
            user=user,
            meal_type=m[0],
            food_name=m[1],
            calories=m[2],
            protein_g=m[3],
            carbs_g=m[4],
            fats_g=m[5],
            date=datetime.now().date()
        )

    print("Seed complete! Demo user created.")

if __name__ == "__main__":
    seed()
