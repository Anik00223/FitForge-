from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    age = models.PositiveIntegerField(null=True, blank=True)
    sex = models.CharField(
        max_length=1,
        choices=[("M", "Male"), ("F", "Female")],
        null=True,
        blank=True,
    )
    weight_kg = models.FloatField(null=True, blank=True)
    height_cm = models.FloatField(null=True, blank=True)
    activity_level = models.CharField(
        max_length=10,
        choices=[
            ("sedentary", "Sedentary"),
            ("light", "Lightly Active"),
            ("moderate", "Moderately Active"),
            ("very", "Very Active"),
        ],
        null=True,
        blank=True,
    )
    fitness_goal = models.CharField(
        max_length=15,
        choices=[
            ("lose", "Lose Weight"),
            ("gain", "Gain Muscle"),
            ("maintain", "Maintain"),
            ("endurance", "Build Endurance"),
        ],
        null=True,
        blank=True,
    )
    dietary_preference = models.CharField(
        max_length=20,
        choices=[
            ("none", "No Preference"),
            ("vegetarian", "Vegetarian"),
            ("vegan", "Vegan"),
            ("keto", "Keto"),
            ("low_carb", "Low Carb"),
            ("high_protein", "High Protein"),
        ],
        default="none",
    )
    allergies = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_complete(self):
        return all(
            [
                self.age,
                self.sex,
                self.weight_kg,
                self.height_cm,
                self.activity_level,
                self.fitness_goal,
            ]
        )

    def __str__(self):
        return f"{self.user.username} profile"

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
        from apps.nutrition.models import DietProfile
        DietProfile.objects.get_or_create(user=instance)
