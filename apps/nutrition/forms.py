from django import forms

from apps.nutrition.models import MealLog


class MealLogForm(forms.ModelForm):
    class Meta:
        model = MealLog
        fields = ["meal_type", "food_name", "calories", "protein_g", "carbs_g", "fats_g"]
