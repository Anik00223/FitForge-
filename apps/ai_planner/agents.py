"""NVIDIA NIM (OpenAI-compatible) agents for FitForge AI plan generation.

Three specialised system prompts drive three distinct plan types:
    - ``generate_diet_plan``     → 7-day Indian meal plan
    - ``generate_fitness_plan``  → 7-day training plan
    - ``generate_combined_plan`` → Combined diet + fitness
    - ``answer_followup``        → Contextual Q&A on an existing plan

Retry strategy: up to 3 attempts with exponential back-off on transient
errors (timeouts, rate limits).  Permanent API errors are raised
immediately so Celery's retry mechanism can decide whether to retry at
the task level.
"""
from __future__ import annotations

import logging
import time

from django.conf import settings
from openai import APIError, APITimeoutError, OpenAI, RateLimitError

logger = logging.getLogger("fitforge.agents")


# ---------------------------------------------------------------------------
# System prompts
# ---------------------------------------------------------------------------
DIET_SYSTEM = """
You are FitForge Diet Specialist, a direct evidence-based nutrition planner.
Build detailed 7-day meal plans using concrete food names and measurable portions.
Use Indian foods prominently where practical: dal, roti, rice, sabzi, paneer, chicken,
eggs, dahi, fruits, sprouts, poha, upma, idli, curd, chutney, and seasonal vegetables.
Respect allergies and dietary preferences. Include calories, protein, carbs, fats per
meal and daily totals. Include hydration, fiber, electrolytes, shopping list, and meal
prep tips. No vague wellness filler.
""".strip()

FITNESS_SYSTEM = """
You are FitForge Fitness Coach, a blunt and practical strength and conditioning coach.
Build structured 7-day training plans with warm-up, main work, cool-down, RPE, rest,
form tips, and progression. Match intensity to activity level and goal. Include 1-2
rest or active recovery days. Use measurable progress tracking. No motivational filler.
""".strip()

TEAM_SYSTEM = """
You are FitForge Health Team. Combine nutrition and fitness into one coherent 7-day
plan. Generate diet first, fitness second. Make sure calorie and macro advice supports
the training load. Be specific, practical, and human.
""".strip()


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _client() -> OpenAI:
    if not settings.NVIDIA_API_KEY:
        raise ValueError("NVIDIA_API_KEY is missing. Add it to your .env file.")
    return OpenAI(base_url=settings.NVIDIA_BASE_URL, api_key=settings.NVIDIA_API_KEY)


def _run_agent(
    system_prompt: str,
    prompt: str,
    max_retries: int = 3,          # FIX: was 1 (= zero retries)
) -> str:
    """Call the NVIDIA NIM API with retry/back-off.

    Args:
        system_prompt: The agent's role definition.
        prompt:        The user-facing request.
        max_retries:   Total attempts (not extra retries).  Defaults to 3.

    Returns:
        The assistant's response text, stripped of leading/trailing whitespace.

    Raises:
        APIError: On a non-retriable API error (bad auth, invalid model, etc.).
        APITimeoutError | RateLimitError: After exhausting all retries.
    """
    client = _client()
    last_exc: Exception | None = None

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=settings.NVIDIA_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.55,
                top_p=0.9,
                timeout=120.0,   # generous for 70B model
            )
            return response.choices[0].message.content.strip()

        except (APITimeoutError, RateLimitError) as exc:
            last_exc = exc
            if attempt < max_retries - 1:
                delay = 2 ** attempt  # 1 s → 2 s → 4 s
                logger.warning(
                    "NVIDIA API transient error (attempt %d/%d), retrying in %ds: %s",
                    attempt + 1, max_retries, delay, exc,
                )
                time.sleep(delay)
            else:
                logger.error(
                    "NVIDIA API failed after %d attempts: %s", max_retries, exc
                )
                raise

        except APIError as exc:
            # Permanent error — don't retry, surface immediately.
            logger.error("NVIDIA API permanent error: %s", exc)
            raise

    # Should be unreachable, but keeps type-checkers happy.
    raise last_exc  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def generate_diet_plan(user_data: dict) -> str:
    try:
        return _run_agent(DIET_SYSTEM, _build_diet_prompt(user_data))
    except Exception as exc:
        logger.exception("generate_diet_plan failed")
        raise RuntimeError(f"Diet plan generation failed: {exc}") from exc


def generate_fitness_plan(user_data: dict) -> str:
    try:
        return _run_agent(FITNESS_SYSTEM, _build_fitness_prompt(user_data))
    except Exception as exc:
        logger.exception("generate_fitness_plan failed")
        raise RuntimeError(f"Fitness plan generation failed: {exc}") from exc


def generate_combined_plan(user_data: dict) -> str:
    try:
        return _run_agent(TEAM_SYSTEM, _build_combined_prompt(user_data))
    except Exception as exc:
        logger.exception("generate_combined_plan failed")
        raise RuntimeError(f"Combined plan generation failed: {exc}") from exc


def answer_followup(plan_content: str, question: str, plan_type: str) -> str:
    if plan_type == "diet":
        system_prompt = DIET_SYSTEM
    elif plan_type == "fitness":
        system_prompt = FITNESS_SYSTEM
    else:
        system_prompt = TEAM_SYSTEM

    prompt = (
        f"The user has this existing FitForge plan:\n\n{plan_content}\n\n"
        f"They are asking this follow-up question:\n{question}\n\n"
        "Answer specifically based on their plan. Be concise, practical, and avoid disclaimers."
    )
    try:
        return _run_agent(system_prompt, prompt)
    except Exception as exc:
        logger.exception("answer_followup failed")
        raise RuntimeError(f"Could not answer question: {exc}") from exc


# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------
def _build_diet_prompt(d: dict) -> str:
    return f"""Generate a complete personalized 7-day Indian diet plan.

USER STATS:
- Age: {d.get('age', 'N/A')} years
- Sex: {d.get('sex', 'N/A')}
- Weight: {d.get('weight_kg', 'N/A')} kg
- Height: {d.get('height_cm', 'N/A')} cm
- Activity Level: {d.get('activity_level', 'N/A')}
- Fitness Goal: {d.get('fitness_goal', 'N/A')}
- Dietary Preference: {d.get('dietary_preference', 'N/A')}
- Allergies/Restrictions: {d.get('allergies') or 'None'}

CALORIE & MACRO TARGETS:
- Daily Calories: {d.get('daily_calories', 'N/A')} kcal
- Protein: {d.get('protein_g', 'N/A')}g
- Carbohydrates: {d.get('carbs_g', 'N/A')}g
- Fats: {d.get('fats_g', 'N/A')}g

Generate the full 7-day plan now."""


def _build_fitness_prompt(d: dict) -> str:
    return f"""Generate a complete personalized 7-day workout plan.

USER STATS:
- Age: {d.get('age', 'N/A')} years
- Sex: {d.get('sex', 'N/A')}
- Weight: {d.get('weight_kg', 'N/A')} kg
- Height: {d.get('height_cm', 'N/A')} cm
- Activity Level: {d.get('activity_level', 'N/A')}
- Fitness Goal: {d.get('fitness_goal', 'N/A')}

Generate the full 7-day workout plan now."""


def _build_combined_prompt(d: dict) -> str:
    return f"""Generate a complete combined 7-day diet AND fitness plan.

USER STATS:
- Age: {d.get('age', 'N/A')} years
- Sex: {d.get('sex', 'N/A')}
- Weight: {d.get('weight_kg', 'N/A')} kg
- Height: {d.get('height_cm', 'N/A')} cm
- Activity Level: {d.get('activity_level', 'N/A')}
- Fitness Goal: {d.get('fitness_goal', 'N/A')}
- Dietary Preference: {d.get('dietary_preference', 'N/A')}
- Allergies: {d.get('allergies') or 'None'}
- Daily Calories: {d.get('daily_calories', 'N/A')} kcal
- Protein: {d.get('protein_g', 'N/A')}g
- Carbs: {d.get('carbs_g', 'N/A')}g
- Fats: {d.get('fats_g', 'N/A')}g

Generate both plans in full, diet first then fitness."""
