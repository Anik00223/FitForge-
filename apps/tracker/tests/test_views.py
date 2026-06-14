"""Tests for the tracker app — BMI logging, workout logging, dashboard."""
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.tracker.models import BMILog, WorkoutLog

User = get_user_model()


def _make_complete_user(username="trackeruser"):
    user = User.objects.create_user(username, password="Str0ngPassw0rd!")
    profile = user.profile
    profile.age = 25
    profile.sex = "M"
    profile.weight_kg = 70.0
    profile.height_cm = 175.0
    profile.activity_level = "moderate"
    profile.fitness_goal = "lose"
    profile.save()
    return user


class TrackerViewsTest(TestCase):
    """Backward-compat original tests."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="password123"
        )
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


class TestDashboardView(TestCase):
    def setUp(self):
        self.user = _make_complete_user("dashboarduser")
        self.client = Client()
        self.client.force_login(self.user)

    def test_dashboard_accessible_complete_profile(self):
        resp = self.client.get(reverse("dashboard"))
        self.assertEqual(resp.status_code, 200)

    def test_dashboard_unauthenticated_redirects(self):
        self.client.logout()
        resp = self.client.get(reverse("dashboard"))
        self.assertRedirects(resp, "/accounts/login/?next=/dashboard/")


class TestBMILogView(TestCase):
    def setUp(self):
        self.user = _make_complete_user("bmiuser")
        self.client = Client()
        self.client.force_login(self.user)
        self.url = reverse("bmi_add")

    def test_valid_bmi_log_creates_record(self):
        self.client.post(self.url, {"weight_kg": 70.0, "height_cm": 175.0})
        self.assertEqual(BMILog.objects.filter(user=self.user).count(), 1)
        log = BMILog.objects.get(user=self.user)
        self.assertAlmostEqual(log.bmi, 22.9, places=0)
        self.assertEqual(log.category, "Normal Weight")

    def test_bmi_log_updates_profile_weight(self):
        self.client.post(self.url, {"weight_kg": 80.0, "height_cm": 175.0})
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.weight_kg, 80.0)


class TestWorkoutLogView(TestCase):
    def setUp(self):
        self.user = _make_complete_user("workoutuser")
        self.client = Client()
        self.client.force_login(self.user)
        self.url = reverse("workout_add")

    def test_valid_workout_creates_record(self):
        self.client.post(
            self.url,
            {
                "exercise": ["Push-ups"],
                "sets": ["3"],
                "reps": ["10"],
                "weight_kg": [""],
                "notes": [""],
            },
        )
        self.assertEqual(WorkoutLog.objects.filter(user=self.user).count(), 1)

    def test_empty_exercise_rejected(self):
        self.client.post(
            self.url,
            {"exercise": [""], "sets": ["3"], "reps": ["10"], "weight_kg": [""], "notes": [""]},
        )
        self.assertEqual(WorkoutLog.objects.filter(user=self.user).count(), 0)

    def test_multiple_exercises_in_one_post(self):
        self.client.post(
            self.url,
            {
                "exercise": ["Squat", "Deadlift"],
                "sets": ["4", "3"],
                "reps": ["8", "5"],
                "weight_kg": ["100", "140"],
                "notes": ["", ""],
            },
        )
        self.assertEqual(WorkoutLog.objects.filter(user=self.user).count(), 2)

    def test_workout_delete_view(self):
        log = WorkoutLog.objects.create(
            user=self.user, exercise="Plank", sets=3, reps=1, weight_kg=None
        )
        self.client.post(reverse("workout_delete", kwargs={"pk": log.pk}))
        self.assertFalse(WorkoutLog.objects.filter(pk=log.pk).exists())

    def test_workout_delete_other_user_forbidden(self):
        other = User.objects.create_user("otherworkout", password="pass123456!")
        log = WorkoutLog.objects.create(user=other, exercise="Run", sets=1, reps=1)
        resp = self.client.post(reverse("workout_delete", kwargs={"pk": log.pk}))
        self.assertEqual(resp.status_code, 404)
