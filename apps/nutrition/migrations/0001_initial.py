from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DietProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("daily_calories_target", models.IntegerField(null=True)),
                ("protein_g", models.IntegerField(null=True)),
                ("carbs_g", models.IntegerField(null=True)),
                ("fats_g", models.IntegerField(null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="diet_profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="MealLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("meal_type", models.CharField(choices=[("breakfast", "Breakfast"), ("lunch", "Lunch"), ("dinner", "Dinner"), ("snack", "Snack")], max_length=10)),
                ("food_name", models.CharField(max_length=200)),
                ("calories", models.IntegerField()),
                ("protein_g", models.FloatField()),
                ("carbs_g", models.FloatField()),
                ("fats_g", models.FloatField()),
                ("date", models.DateField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="meal_logs", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-date"]},
        ),
        migrations.AddIndex(model_name="meallog", index=models.Index(fields=["user", "-date"], name="nutrition_m_user_id_67cf95_idx")),
    ]
