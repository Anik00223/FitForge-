from django.contrib import admin
from apps.nutrition.models import DietProfile, MealLog

@admin.register(DietProfile)
class DietProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'daily_calories_target', 'protein_g', 'carbs_g', 'fats_g')
    search_fields = ('user__username',)

@admin.register(MealLog)
class MealLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'meal_type', 'food_name', 'calories', 'protein_g', 'carbs_g', 'fats_g', 'date')
    list_filter = ('meal_type', 'date')
    search_fields = ('user__username', 'food_name')
    date_hierarchy = 'date'
