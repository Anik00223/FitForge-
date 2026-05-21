from django.urls import path

from apps.nutrition import views


urlpatterns = [
    path("meal-log/", views.meal_log_view, name="meal_log"),
    path("meal-log/delete/<int:pk>/", views.delete_meal, name="delete_meal"),
]
