from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class TrackerViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", email="test@test.com", password="password123")
        self.client.login(username="testuser", password="password123")

    def test_dashboard_access(self):
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(response, reverse("profile_setup"))

    def test_bmi_add_view_get(self):
        response = self.client.get(reverse("bmi_add"))
        self.assertEqual(response.status_code, 200)

    def test_bmi_add_view_post(self):
        response = self.client.post(reverse("bmi_add"), {"weight_kg": 80, "height_cm": 180})
        self.assertRedirects(response, reverse("bmi_history"))
        
    def test_workout_add_view_get(self):
        response = self.client.get(reverse("workout_add"))
        self.assertEqual(response.status_code, 200)
        
    def test_workout_history_view(self):
        response = self.client.get(reverse("workout_history"))
        self.assertEqual(response.status_code, 200)
