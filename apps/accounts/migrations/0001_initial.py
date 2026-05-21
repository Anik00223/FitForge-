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
            name="UserProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("age", models.PositiveIntegerField(blank=True, null=True)),
                ("sex", models.CharField(blank=True, choices=[("M", "Male"), ("F", "Female")], max_length=1, null=True)),
                ("weight_kg", models.FloatField(blank=True, null=True)),
                ("height_cm", models.FloatField(blank=True, null=True)),
                ("activity_level", models.CharField(blank=True, choices=[("sedentary", "Sedentary"), ("light", "Lightly Active"), ("moderate", "Moderately Active"), ("very", "Very Active")], max_length=10, null=True)),
                ("fitness_goal", models.CharField(blank=True, choices=[("lose", "Lose Weight"), ("gain", "Gain Muscle"), ("maintain", "Maintain"), ("endurance", "Build Endurance")], max_length=15, null=True)),
                ("dietary_preference", models.CharField(choices=[("none", "No Preference"), ("vegetarian", "Vegetarian"), ("vegan", "Vegan"), ("keto", "Keto"), ("low_carb", "Low Carb"), ("high_protein", "High Protein")], default="none", max_length=20)),
                ("allergies", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
