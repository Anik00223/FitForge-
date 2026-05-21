import markdown
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.ai_planner.agents import (
    answer_followup,
    generate_combined_plan,
    generate_diet_plan,
    generate_fitness_plan,
)
from apps.ai_planner.models import GeneratedPlan, PlanQA
from core.decorators import login_required_custom
from core.rate_limit import rate_limit


def _user_data(user):
    profile = user.profile
    diet = getattr(user, "diet_profile", None)
    return {
        "age": profile.age,
        "sex": profile.get_sex_display() if profile.sex else "N/A",
        "weight_kg": profile.weight_kg,
        "height_cm": profile.height_cm,
        "activity_level": profile.get_activity_level_display() if profile.activity_level else "N/A",
        "fitness_goal": profile.get_fitness_goal_display() if profile.fitness_goal else "N/A",
        "dietary_preference": profile.get_dietary_preference_display(),
        "allergies": profile.allergies,
        "daily_calories": diet.daily_calories_target if diet else None,
        "protein_g": diet.protein_g if diet else None,
        "carbs_g": diet.carbs_g if diet else None,
        "fats_g": diet.fats_g if diet else None,
    }


def _render_markdown(text):
    return markdown.markdown(text, extensions=["tables", "fenced_code", "nl2br"])


@login_required_custom
@rate_limit(key_prefix="planner_generate", limit=5, window=86400) # 5 plans per day
def planner_view(request):
    profile = request.user.profile
    if not profile.is_complete():
        messages.warning(request, "Complete your profile first so the AI plan is actually personal.")
        return redirect("profile_setup")

    active_plan = GeneratedPlan.objects.filter(user=request.user, is_active=True).first()
    plan_html = _render_markdown(active_plan.plan_content) if active_plan else ""

    if request.method == "POST":
        plan_type = request.POST.get("plan_type", "combined")
        data = _user_data(request.user)
        if plan_type == "diet":
            content = generate_diet_plan(data)
        elif plan_type == "fitness":
            content = generate_fitness_plan(data)
        else:
            plan_type = "combined"
            content = generate_combined_plan(data)

        if "failed:" in content.lower():
            messages.error(request, content)
            return redirect("planner")

        GeneratedPlan.objects.filter(user=request.user).update(is_active=False)
        plan = GeneratedPlan.objects.create(
            user=request.user,
            plan_type=plan_type,
            plan_content=content,
            user_inputs=data,
            is_active=True,
        )
        messages.success(request, "Your FitForge plan is ready.")
        return redirect("view_plan", pk=plan.pk)

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


@login_required_custom
def history_view(request):
    plans = GeneratedPlan.objects.filter(user=request.user)
    return render(request, "ai_planner/history.html", {"plans": plans})


@login_required_custom
def view_plan(request, pk):
    plan = get_object_or_404(GeneratedPlan, pk=pk, user=request.user)
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
def delete_plan(request, pk):
    plan = get_object_or_404(GeneratedPlan, pk=pk, user=request.user)
    if request.method == "POST":
        plan.delete()
        messages.success(request, "Plan deleted.")
    return redirect("plan_history")


@login_required_custom
@rate_limit(key_prefix="planner_qa", limit=20, window=3600) # 20 questions per hour
def ask_followup_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required."}, status=400)
    plan_id = request.POST.get("plan_id")
    question = request.POST.get("question", "").strip()
    if not plan_id or not question:
        return JsonResponse({"error": "Plan and question are required."}, status=400)
    plan = get_object_or_404(GeneratedPlan, pk=plan_id, user=request.user)
    answer = answer_followup(plan.plan_content, question, plan.plan_type)
    if answer.lower().startswith("could not answer"):
        return JsonResponse({"error": answer}, status=400)
    qa = PlanQA.objects.create(plan=plan, question=question, answer=answer)
    return JsonResponse(
        {
            "question": qa.question,
            "answer": _render_markdown(qa.answer),
        }
    )
