from django.conf import settings
from django.db import models


class GeneratedPlan(models.Model):
    PLAN_TYPES = [
        ("diet", "Diet Plan"),
        ("fitness", "Fitness Plan"),
        ("combined", "Combined Plan"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="generated_plans",
    )
    plan_type = models.CharField(max_length=10, choices=PLAN_TYPES)
    plan_content = models.TextField()
    user_inputs = models.JSONField()
    is_active = models.BooleanField(default=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-generated_at"]

    def __str__(self):
        return f"{self.get_plan_type_display()} - {self.user.username}"


class PlanQA(models.Model):
    plan = models.ForeignKey(
        GeneratedPlan,
        on_delete=models.CASCADE,
        related_name="qa_history",
    )
    question = models.TextField()
    answer = models.TextField()
    asked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["asked_at"]

    def __str__(self):
        return self.question[:80]
