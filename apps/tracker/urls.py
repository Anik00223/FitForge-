from django.urls import path

from apps.tracker import views


urlpatterns = [
    path("", views.home_view, name="tracker_home"),
    path("dashboard/", views.dashboard_view, name="tracker_dashboard"),
    path("bmi/add/", views.bmi_add_view, name="bmi_add"),
    path("bmi/history/", views.bmi_history_view, name="bmi_history"),
    path("workout/add/", views.workout_add_view, name="workout_add"),
    path("workout/history/", views.workout_history_view, name="workout_history"),
    path("workout/delete/<int:pk>/", views.workout_delete_view, name="workout_delete"),
]
