from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from apps.ai_planner.models import GeneratedPlan

class AIPlannerViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", email="test@test.com", password="password123")
        self.client.login(username="testuser", password="password123")
        
        # Complete profile to access planner
        profile = self.user.profile
        profile.age = 25
        profile.sex = "M"
        profile.weight_kg = 75.0
        profile.height_cm = 180.0
        profile.activity_level = "moderate"
        profile.fitness_goal = "gain"
        profile.save()

    def test_planner_view_get(self):
        response = self.client.get(reverse("planner"))
        self.assertEqual(response.status_code, 200)

    @patch("apps.ai_planner.views.generate_combined_plan")
    def test_planner_view_post(self, mock_generate):
        mock_generate.return_value = "Mocked AI Plan Content"
        response = self.client.post(reverse("planner"), {"plan_type": "combined"})
        
        self.assertTrue(GeneratedPlan.objects.filter(user=self.user).exists())
        plan = GeneratedPlan.objects.get(user=self.user)
        self.assertRedirects(response, reverse("view_plan", kwargs={"pk": plan.pk}))
        self.assertEqual(plan.plan_content, "Mocked AI Plan Content")
        
    def test_plan_history(self):
        response = self.client.get(reverse("plan_history"))
        self.assertEqual(response.status_code, 200)
