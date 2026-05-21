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
            name="GeneratedPlan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("plan_type", models.CharField(choices=[("diet", "Diet Plan"), ("fitness", "Fitness Plan"), ("combined", "Combined Plan")], max_length=10)),
                ("plan_content", models.TextField()),
                ("user_inputs", models.JSONField()),
                ("is_active", models.BooleanField(default=True)),
                ("generated_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="generated_plans", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-generated_at"]},
        ),
        migrations.CreateModel(
            name="PlanQA",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("question", models.TextField()),
                ("answer", models.TextField()),
                ("asked_at", models.DateTimeField(auto_now_add=True)),
                ("plan", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="qa_history", to="ai_planner.generatedplan")),
            ],
            options={"ordering": ["asked_at"]},
        ),
    ]
