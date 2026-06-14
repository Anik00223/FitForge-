"""Views for the AI planner app.

Plan generation is now fully asynchronous via Celery:
  1. User POSTs to ``planner_view`` → plan row created (PENDING)
  2. Celery task dispatched → user redirected to ``plan_status`` page
  3. ``plan_status_api`` is polled every 3 s via JS until DONE or FAILED
  4. On DONE, page redirects to ``view_plan``
"""
from __future__ import annotations

import logging
from typing import Any

import markdown
import bleach
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.ai_planner.models import GeneratedPlan, PlanQA
from apps.ai_planner.tasks import generate_plan_task
from core.decorators import login_required_custom
from core.rate_limit import rate_limit

logger = logging.getLogger("fitforge.ai_planner")


# ---------------------------------------------------------------------------
# Markdown rendering (sanitised)
# ---------------------------------------------------------------------------
_ALLOWED_TAGS = [
    "p", "br", "strong", "em", "ul", "ol", "li",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "table", "thead", "tbody", "tr", "th", "td",
    "code", "pre", "blockquote", "a",
]
_ALLOWED_ATTRS = {"a": ["href", "title"], "*": ["class"]}


def _render_markdown(text: str) -> str:
    html = markdown.markdown(text, extensions=["tables", "fenced_code", "nl2br"])
    return bleach.clean(html, tags=_ALLOWED_TAGS, attributes=_ALLOWED_ATTRS, strip=True)


# ---------------------------------------------------------------------------
# User data helper
# ---------------------------------------------------------------------------
def _user_data(user) -> dict[str, Any]:
    profile = getattr(user, "profile", None)
    if not profile:
        return {}
    diet = getattr(user, "diet_profile", None)
    return {
        "age": getattr(profile, "age", None),
        "sex": profile.get_sex_display() if getattr(profile, "sex", None) else "N/A",
        "weight_kg": getattr(profile, "weight_kg", None),
        "height_cm": getattr(profile, "height_cm", None),
        "activity_level": (
            profile.get_activity_level_display()
            if getattr(profile, "activity_level", None)
            else "N/A"
        ),
        "fitness_goal": (
            profile.get_fitness_goal_display()
            if getattr(profile, "fitness_goal", None)
            else "N/A"
        ),
        "dietary_preference": (
            profile.get_dietary_preference_display()
            if hasattr(profile, "get_dietary_preference_display")
            else "N/A"
        ),
        "allergies": getattr(profile, "allergies", ""),
        "daily_calories": diet.daily_calories_target if diet else None,
        "protein_g": float(diet.protein_g) if diet and diet.protein_g else None,
        "carbs_g": float(diet.carbs_g) if diet and diet.carbs_g else None,
        "fats_g": float(diet.fats_g) if diet and diet.fats_g else None,
    }


# ---------------------------------------------------------------------------
# Main planner view
# ---------------------------------------------------------------------------
@login_required_custom
@rate_limit(key_prefix="planner_generate", limit=5, window=86400, html_redirect=True)
def planner_view(request):
    profile = request.user.profile
    if not profile.is_complete():
        messages.warning(
            request,
            "Complete your profile first so the AI plan is actually personal.",
        )
        return redirect("profile_setup")

    active_plan = GeneratedPlan.objects.filter(
        user=request.user, is_active=True, status=GeneratedPlan.Status.DONE
    ).first()
    plan_html = _render_markdown(active_plan.plan_content) if active_plan else ""

    if request.method == "POST":
        plan_type = request.POST.get("plan_type", "combined")
        if plan_type not in ("diet", "fitness", "combined"):
            plan_type = "combined"

        data = _user_data(request.user)

        # Create the plan row in PENDING state immediately.
        plan = GeneratedPlan.objects.create(
            user=request.user,
            plan_type=plan_type,
            user_inputs=data,
            status=GeneratedPlan.Status.PENDING,
            is_active=False,
        )

        # Dispatch to Celery — returns immediately, no blocking.
        generate_plan_task.delay(plan.pk)

        messages.info(
            request,
            "Your FitForge plan is being generated — this takes about 30–60 seconds.",
        )
        return redirect("plan_status", pk=plan.pk)

    return render(
        request,
        "ai_planner/planner.html",
        {
            "profile": profile,
            "diet_profile": getattr(request.user, "diet_profile", None),
            "active_plan": active_plan,
            "plan_html": plan_html,
        },
    )


# ---------------------------------------------------------------------------
# Async status page + polling API
# ---------------------------------------------------------------------------
@login_required_custom
def plan_status_view(request, pk: int):
    """Rendered page that JS polls until the plan is ready."""
    plan = get_object_or_404(GeneratedPlan, pk=pk, user=request.user)
    if plan.status == GeneratedPlan.Status.DONE:
        return redirect("view_plan", pk=plan.pk)
    return render(request, "ai_planner/plan_status.html", {"plan": plan})


@login_required_custom
def plan_status_api(request, pk: int):
    """JSON polling endpoint called by the status page every 3 s."""
    plan = get_object_or_404(GeneratedPlan, pk=pk, user=request.user)
    data: dict[str, Any] = {
        "status": plan.status,
        "done": plan.status == GeneratedPlan.Status.DONE,
        "failed": plan.status == GeneratedPlan.Status.FAILED,
        "error": plan.error_message if plan.status == GeneratedPlan.Status.FAILED else "",
    }
    if data["done"]:
        data["redirect_url"] = f"/planner/plan/{plan.pk}/"
    return JsonResponse(data)


# ---------------------------------------------------------------------------
# View / history / delete
# ---------------------------------------------------------------------------
@login_required_custom
def history_view(request):
    qs = GeneratedPlan.objects.filter(user=request.user)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "ai_planner/history.html", {"page_obj": page_obj})


@login_required_custom
def view_plan(request, pk: int):
    plan = get_object_or_404(
        GeneratedPlan, pk=pk, user=request.user, status=GeneratedPlan.Status.DONE
    )
    return render(
        request,
        "ai_planner/planner.html",
        {
            "profile": request.user.profile,
            "diet_profile": getattr(request.user, "diet_profile", None),
            "active_plan": plan,
            "plan_html": _render_markdown(plan.plan_content),
        },
    )


@login_required_custom
def delete_plan(request, pk: int):
    plan = get_object_or_404(GeneratedPlan, pk=pk, user=request.user)
    if request.method == "POST":
        plan.delete()
        messages.success(request, "Plan deleted.")
    return redirect("plan_history")


# ---------------------------------------------------------------------------
# Follow-up Q&A
# ---------------------------------------------------------------------------
@login_required_custom
@rate_limit(key_prefix="planner_qa", limit=20, window=3600)
def ask_followup_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required."}, status=400)

    plan_id = request.POST.get("plan_id")
    question = request.POST.get("question", "").strip()
    if not plan_id or not question:
        return JsonResponse({"error": "Plan and question are required."}, status=400)

    plan = get_object_or_404(
        GeneratedPlan, pk=plan_id, user=request.user, status=GeneratedPlan.Status.DONE
    )

    from apps.ai_planner.agents import answer_followup
    try:
        answer = answer_followup(plan.plan_content, question, plan.plan_type)
    except Exception as exc:
        logger.exception("ask_followup_view failed plan_id=%s", plan_id)
        return JsonResponse({"error": str(exc)}, status=500)

    qa = PlanQA.objects.create(plan=plan, question=question, answer=answer)
    return JsonResponse(
        {
            "question": qa.question,
            "answer": _render_markdown(qa.answer),
        }
    )
