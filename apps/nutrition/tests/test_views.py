from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class NutritionViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", email="test@test.com", password="password123")
        self.client.login(username="testuser", password="password123")

    def test_meal_log_view_get(self):
        response = self.client.get(reverse("meal_log"))
        self.assertEqual(response.status_code, 200)

    def test_meal_log_view_post(self):
        response = self.client.post(reverse("meal_log"), {
            "meal_type": "Breakfast",
            "food_name": "Oats",
            "calories": 300,
            "protein_g": 10,
            "carbs_g": 50,
            "fats_g": 5
        })
        self.assertRedirects(response, reverse("meal_log"))
