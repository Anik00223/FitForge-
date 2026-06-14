"""Celery tasks for AI plan generation.

These tasks run in the Celery worker process, completely off the
gunicorn/ASGI request thread.  The view creates a ``GeneratedPlan``
row in PENDING state, dispatches the task, and immediately redirects
the user to a polling page — so no HTTP worker is blocked for 30-45 s.

Retry strategy:
    * Up to 3 automatic retries with exponential back-off.
    * Countdown starts at 10 s, doubling on each retry (10 → 20 → 40).
    * After exhausting retries the plan is marked FAILED with the
      error message so the UI can surface a useful message.
"""
from __future__ import annotations

import logging

from celery import shared_task
from django.utils import timezone

from apps.ai_planner import agents
from apps.ai_planner.models import GeneratedPlan

logger = logging.getLogger("fitforge.ai_planner")


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    acks_late=True,          # only ack after successful processing
    reject_on_worker_lost=True,
)
def generate_plan_task(self, plan_id: int) -> None:
    """Generate an AI plan for the ``GeneratedPlan`` row identified by *plan_id*.

    The plan row must already exist in the database in PENDING state.
    This task updates it to GENERATING → DONE (or FAILED).
    """
    try:
        plan = GeneratedPlan.objects.get(pk=plan_id)
    except GeneratedPlan.DoesNotExist:
        logger.error("generate_plan_task: plan_id=%d not found — aborting.", plan_id)
        return  # nothing to mark failed; row doesn't exist

    # Mark as generating so the polling endpoint can reflect progress.
    plan.status = GeneratedPlan.Status.GENERATING
    plan.save(update_fields=["status"])

    user_data: dict = plan.user_inputs
    plan_type: str = plan.plan_type

    logger.info(
        "generate_plan_task starting plan_id=%d user=%s type=%s attempt=%d",
        plan_id,
        plan.user_id,
        plan_type,
        self.request.retries + 1,
    )

    try:
        if plan_type == "diet":
            content = agents.generate_diet_plan(user_data)
        elif plan_type == "fitness":
            content = agents.generate_fitness_plan(user_data)
        else:
            content = agents.generate_combined_plan(user_data)

        if not content or "failed:" in content.lower():
            raise ValueError(f"Agent returned failure content: {content[:200]}")

        # Deactivate all previous plans for this user, then mark this one done.
        GeneratedPlan.objects.filter(
            user_id=plan.user_id, is_active=True
        ).exclude(pk=plan_id).update(is_active=False)

        plan.plan_content = content
        plan.status = GeneratedPlan.Status.DONE
        plan.is_active = True
        plan.save(update_fields=["plan_content", "status", "is_active"])

        logger.info("generate_plan_task completed plan_id=%d", plan_id)

    except Exception as exc:
        logger.warning(
            "generate_plan_task failed plan_id=%d attempt=%d error=%s",
            plan_id,
            self.request.retries + 1,
            str(exc),
        )
        try:
            # Retry with exponential back-off.
            raise self.retry(exc=exc, countdown=10 * (2 ** self.request.retries))
        except self.MaxRetriesExceededError:
            logger.error(
                "generate_plan_task exhausted retries plan_id=%d error=%s",
                plan_id,
                str(exc),
            )
            plan.status = GeneratedPlan.Status.FAILED
            plan.error_message = str(exc)[:500]
            plan.save(update_fields=["status", "error_message"])
