from django.conf import settings
from django.db import models


class DietProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="diet_profile",
    )
    daily_calories_target = models.IntegerField(null=True)
    protein_g = models.IntegerField(null=True)
    carbs_g = models.IntegerField(null=True)
    fats_g = models.IntegerField(null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} diet targets"


class MealLog(models.Model):
    MEAL_CHOICES = [
        ("breakfast", "Breakfast"),
        ("lunch", "Lunch"),
        ("dinner", "Dinner"),
        ("snack", "Snack"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="meal_logs",
    )
    meal_type = models.CharField(max_length=10, choices=MEAL_CHOICES)
    food_name = models.CharField(max_length=200)
    calories = models.IntegerField()
    protein_g = models.FloatField()
    carbs_g = models.FloatField()
    fats_g = models.FloatField()
    date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]
        indexes = [models.Index(fields=["user", "-date"])]

    def __str__(self):
        return f"{self.food_name} - {self.user.username}"
