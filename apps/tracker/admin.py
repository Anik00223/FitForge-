from django.contrib import admin
from apps.tracker.models import BMILog, WorkoutLog

@admin.register(BMILog)
class BMILogAdmin(admin.ModelAdmin):
    list_display = ('user', 'bmi', 'category', 'weight_kg', 'height_cm', 'date')
    list_filter = ('category', 'date')
    search_fields = ('user__username',)
    date_hierarchy = 'date'

@admin.register(WorkoutLog)
class WorkoutLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'exercise', 'sets', 'reps', 'weight_kg', 'date')
    list_filter = ('date',)
    search_fields = ('user__username', 'exercise')
    date_hierarchy = 'date'
