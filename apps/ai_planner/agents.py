import time
import logging
from django.conf import settings
from openai import OpenAI, APIError, APITimeoutError, RateLimitError

logger = logging.getLogger(__name__)


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


def _client():
    if not settings.NVIDIA_API_KEY:
        raise ValueError("NVIDIA_API_KEY is missing. Add it to your .env file.")
    return OpenAI(base_url=settings.NVIDIA_BASE_URL, api_key=settings.NVIDIA_API_KEY)


def _run_agent(system_prompt: str, prompt: str, max_retries: int = 1) -> str:
    client = _client()
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
                timeout=45.0,  # 45 second timeout for fast model
            )
            return response.choices[0].message.content.strip()
        except (APITimeoutError, RateLimitError) as e:
            if attempt == max_retries - 1:
                logger.error(f"NVIDIA API failed after {max_retries} attempts: {str(e)}")
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
        except APIError as e:
            logger.error(f"NVIDIA API Error: {str(e)}")
            raise


def generate_diet_plan(user_data: dict) -> str:
    try:
        prompt = _build_diet_prompt(user_data)
        return _run_agent(DIET_SYSTEM, prompt)
    except Exception as e:
        return f"Diet plan generation failed: {str(e)}"


def generate_fitness_plan(user_data: dict) -> str:
    try:
        prompt = _build_fitness_prompt(user_data)
        return _run_agent(FITNESS_SYSTEM, prompt)
    except Exception as e:
        return f"Fitness plan generation failed: {str(e)}"


def generate_combined_plan(user_data: dict) -> str:
    try:
        prompt = _build_combined_prompt(user_data)
        return _run_agent(TEAM_SYSTEM, prompt)
    except Exception as e:
        return f"Combined plan generation failed: {str(e)}"


def answer_followup(plan_content: str, question: str, plan_type: str) -> str:
    try:
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
        return _run_agent(system_prompt, prompt)
    except Exception as e:
        return f"Could not answer question: {str(e)}"


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
