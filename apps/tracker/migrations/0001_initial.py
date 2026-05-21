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
            name="BMILog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("weight_kg", models.FloatField()),
                ("height_cm", models.FloatField()),
                ("bmi", models.FloatField()),
                ("category", models.CharField(max_length=20)),
                ("date", models.DateField(auto_now_add=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="bmi_logs", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-date"]},
        ),
        migrations.CreateModel(
            name="WorkoutLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("exercise", models.CharField(max_length=200)),
                ("sets", models.PositiveIntegerField()),
                ("reps", models.PositiveIntegerField()),
                ("weight_kg", models.FloatField(blank=True, null=True)),
                ("notes", models.TextField(blank=True)),
                ("date", models.DateField(auto_now_add=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="workout_logs", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-date"]},
        ),
        migrations.AddIndex(model_name="bmilog", index=models.Index(fields=["user", "-date"], name="tracker_bmi_user_id_8f5b7c_idx")),
        migrations.AddIndex(model_name="workoutlog", index=models.Index(fields=["user", "-date"], name="tracker_wor_user_id_c93b4b_idx")),
    ]
