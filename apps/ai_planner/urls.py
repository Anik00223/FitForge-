from django.urls import path

from apps.ai_planner import views


urlpatterns = [
    path("", views.planner_view, name="planner"),
    path("history/", views.history_view, name="plan_history"),
    path("plan/<int:pk>/", views.view_plan, name="view_plan"),
    path("plan/<int:pk>/status/", views.plan_status_view, name="plan_status"),
    path("plan/<int:pk>/status/api/", views.plan_status_api, name="plan_status_api"),
    path("delete/<int:pk>/", views.delete_plan, name="delete_plan"),
    path("ask/", views.ask_followup_view, name="ask_followup"),
]
