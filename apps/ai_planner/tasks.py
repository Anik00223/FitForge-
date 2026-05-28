"""
Background tasks for AI plan generation using a simple threading approach
and future-ready Celery integration.
"""
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.ai_planner import agents
from apps.ai_planner.models import GeneratedPlan

User = get_user_model()

_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="fitforge_ai_")


class PlanGenerationResult:
    """Result wrapper for async plan generation."""

    def __init__(self, success: bool, content: str, plan_type: str, error: Optional[str] = None):
        self.success = success
        self.content = content
        self.plan_type = plan_type
        self.error = error
        self.generated_at = timezone.now()


def _run_generation(user_data: dict, plan_type: str) -> PlanGenerationResult:
    """Synchronous helper that dispatches to the correct agent."""
    try:
        if plan_type == "diet":
            content = agents.generate_diet_plan(user_data)
        elif plan_type == "fitness":
            content = agents.generate_fitness_plan(user_data)
        else:
            content = agents.generate_combined_plan(user_data)
        return PlanGenerationResult(success="failed" not in content.lower(), content=content, plan_type=plan_type)
    except Exception as e:
        return PlanGenerationResult(success=False, content="", plan_type=plan_type, error=str(e))


def generate_ai_plan_async(user_id: int, user_data: dict, plan_type: str = "combined") -> None:
    """Kick off AI plan generation in a background thread."""
    from apps.ai_planner.models import GeneratedPlan

    def _task():
        result = _run_generation(user_data, plan_type)
        if result.success:
            GeneratedPlan.objects.create(
                user_id=user_id,
                plan_type=plan_type,
                plan_content=result.content,
                user_inputs=user_data,
                is_active=True,
            )

    _executor.submit(_task)
