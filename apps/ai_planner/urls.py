from django.urls import path

from apps.ai_planner import views


urlpatterns = [
    path("", views.planner_view, name="planner"),
    path("history/", views.history_view, name="plan_history"),
    path("view/<int:pk>/", views.view_plan, name="view_plan"),
    path("delete/<int:pk>/", views.delete_plan, name="delete_plan"),
    path("ask/", views.ask_followup_view, name="ask_followup"),
]
