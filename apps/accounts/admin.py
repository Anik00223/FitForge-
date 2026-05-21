from django.contrib import admin
from apps.accounts.models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'sex', 'weight_kg', 'height_cm', 'activity_level', 'fitness_goal')
    list_filter = ('sex', 'activity_level', 'fitness_goal', 'dietary_preference')
    search_fields = ('user__username', 'user__email')
