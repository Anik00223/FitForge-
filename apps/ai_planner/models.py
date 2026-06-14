from django.conf import settings
from django.db import models


class GeneratedPlan(models.Model):
    PLAN_TYPES = [
        ("diet", "Diet Plan"),
        ("fitness", "Fitness Plan"),
        ("combined", "Combined Plan"),
    ]

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        GENERATING = "generating", "Generating"
        DONE = "done", "Done"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="generated_plans",
    )
    plan_type = models.CharField(max_length=10, choices=PLAN_TYPES)
    plan_content = models.TextField(blank=True, default="")
    user_inputs = models.JSONField(default=dict)
    is_active = models.BooleanField(default=False)
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    error_message = models.TextField(blank=True, default="")
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-generated_at"]
        indexes = [
            models.Index(fields=["user", "-generated_at"]),
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self):
        return f"{self.get_plan_type_display()} [{self.status}] - {self.user.username}"

    @property
    def is_ready(self) -> bool:
        return self.status == self.Status.DONE

    @property
    def is_pending(self) -> bool:
        return self.status in (self.Status.PENDING, self.Status.GENERATING)


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
