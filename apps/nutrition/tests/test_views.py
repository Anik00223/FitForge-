"""Tests for the nutrition app — meal logging, diet profile."""
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.nutrition.models import DietProfile, MealLog

User = get_user_model()


class NutritionViewsTest(TestCase):
    """Backward-compat original tests."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="password123"
        )
        self.client.login(username="testuser", password="password123")

    def test_meal_log_view_get(self):
        response = self.client.get(reverse("meal_log"))
        self.assertEqual(response.status_code, 200)

    def test_meal_log_view_post(self):
        response = self.client.post(
            reverse("meal_log"),
            {
                "meal_type": "breakfast",
                "food_name": "Oats",
                "calories": 300,
                "protein_g": 10,
                "carbs_g": 50,
                "fats_g": 5,
            },
        )
        self.assertRedirects(response, reverse("meal_log"))


class TestMealLogCRUD(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("mealuser", password="Str0ngPassw0rd!")
        self.client = Client()
        self.client.force_login(self.user)
        self.url = reverse("meal_log")

    def test_valid_meal_log_creates_record(self):
        self.client.post(
            self.url,
            {
                "meal_type": "lunch",
                "food_name": "Dal Chawal",
                "calories": 450,
                "protein_g": 15.5,
                "carbs_g": 70.0,
                "fats_g": 8.5,
            },
        )
        self.assertEqual(MealLog.objects.filter(user=self.user).count(), 1)
        log = MealLog.objects.get(user=self.user)
        self.assertEqual(log.food_name, "Dal Chawal")
        self.assertEqual(float(log.protein_g), 15.5)

    def test_decimal_precision_preserved(self):
        """Verify DecimalField preserves fractional macros (old IntegerField rounded them)."""
        self.client.post(
            self.url,
            {
                "meal_type": "snack",
                "food_name": "Paneer",
                "calories": 200,
                "protein_g": 14.3,
                "carbs_g": 3.7,
                "fats_g": 15.6,
            },
        )
        log = MealLog.objects.get(user=self.user, food_name="Paneer")
        self.assertEqual(float(log.protein_g), 14.3)
        self.assertEqual(float(log.carbs_g), 3.7)
        self.assertEqual(float(log.fats_g), 15.6)

    def test_meal_unauthenticated_redirects(self):
        self.client.logout()
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp["Location"])


class TestDietProfile(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("dietuser", password="Str0ngPassw0rd!")

    def test_diet_profile_auto_created(self):
        self.assertTrue(DietProfile.objects.filter(user=self.user).exists())

    def test_diet_profile_decimal_fields(self):
        """DietProfile macro fields should accept decimal values."""
        diet = self.user.diet_profile
        diet.protein_g = 147.5
        diet.carbs_g = 203.3
        diet.fats_g = 66.7
        diet.daily_calories_target = 2000
        diet.save()
        diet.refresh_from_db()
        self.assertEqual(float(diet.protein_g), 147.5)
        self.assertEqual(float(diet.carbs_g), 203.3)
