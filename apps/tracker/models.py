from django.conf import settings
from django.db import models


class BMILog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bmi_logs",
    )
    weight_kg = models.FloatField()
    height_cm = models.FloatField()
    bmi = models.FloatField()
    category = models.CharField(max_length=20)
    date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]
        indexes = [models.Index(fields=["user", "-date"])]

    def __str__(self):
        return f"{self.user.username} BMI {self.bmi}"


class WorkoutLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workout_logs",
    )
    exercise = models.CharField(max_length=200)
    sets = models.PositiveIntegerField()
    reps = models.PositiveIntegerField()
    weight_kg = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True)
    date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]
        indexes = [models.Index(fields=["user", "-date"])]

    def __str__(self):
        return f"{self.exercise} - {self.user.username}"
