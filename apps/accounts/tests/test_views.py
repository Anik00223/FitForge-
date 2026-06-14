"""Tests for the accounts app — signup, login, profile setup."""
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.accounts.models import UserProfile
from apps.nutrition.models import DietProfile

User = get_user_model()


class TestSignupView(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("signup")

    def test_get_renders_form(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "form")

    def test_valid_signup_creates_user(self):
        resp = self.client.post(
            self.url,
            {
                "name": "Test User",
                "email": "testuser2@example.com",
                "password": "Str0ngPassw0rd!",
                "confirm_password": "Str0ngPassw0rd!",
            },
        )
        # User is created with email as username (see forms.py SignupForm.save)
        self.assertTrue(
            User.objects.filter(email="testuser2@example.com").exists(),
            msg=f"User not created. Response: {resp.status_code}",
        )

    def test_valid_signup_creates_profile_and_diet_profile(self):
        self.client.post(
            self.url,
            {
                "name": "Profile Test",
                "email": "profile@example.com",
                "password": "Str0ngPassw0rd!",
                "confirm_password": "Str0ngPassw0rd!",
            },
        )
        user = User.objects.filter(email="profile@example.com").first()
        if user:
            self.assertTrue(UserProfile.objects.filter(user=user).exists())
            self.assertTrue(DietProfile.objects.filter(user=user).exists())

    def test_authenticated_user_redirected(self):
        user = User.objects.create_user("existing", password="pass1234word!")
        self.client.force_login(user)
        resp = self.client.get(self.url)
        self.assertRedirects(resp, reverse("dashboard"), fetch_redirect_response=False)


class TestLoginView(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("login")
        self.user = User.objects.create_user(
            username="loginuser", password="Str0ngPassw0rd!"
        )

    def test_get_renders_form(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_authenticated_user_redirected(self):
        self.client.force_login(self.user)
        resp = self.client.get(self.url)
        self.assertRedirects(resp, reverse("dashboard"), fetch_redirect_response=False)


class TestUserProfileSignal(TestCase):
    def test_profile_auto_created_on_user_save(self):
        user = User.objects.create_user("auto_profile_user", password="pass12345678!")
        self.assertTrue(hasattr(user, "profile"))
        self.assertIsInstance(user.profile, UserProfile)

    def test_diet_profile_auto_created_on_user_save(self):
        user = User.objects.create_user("auto_diet_user", password="pass12345678!")
        self.assertTrue(hasattr(user, "diet_profile"))
        self.assertIsInstance(user.diet_profile, DietProfile)


class TestProfileSetupView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("setup_user", password="Str0ngPassw0rd!")
        self.client.force_login(self.user)
        self.url = reverse("profile_setup")

    def test_get_renders_form(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_valid_profile_saves_and_redirects(self):
        resp = self.client.post(
            self.url,
            {
                "age": 25,
                "sex": "M",
                "weight_kg": 70.0,
                "height_cm": 175.0,
                "activity_level": "moderate",
                "fitness_goal": "lose",
                "dietary_preference": "none",
                "allergies": "",
            },
        )
        self.assertRedirects(resp, reverse("planner"))
        profile = self.user.profile
        profile.refresh_from_db()
        self.assertEqual(profile.age, 25)
        self.assertEqual(profile.sex, "M")

    def test_profile_is_complete_method(self):
        profile = self.user.profile
        self.assertFalse(profile.is_complete())
        profile.age = 25
        profile.sex = "M"
        profile.weight_kg = 70.0
        profile.height_cm = 175.0
        profile.activity_level = "moderate"
        profile.fitness_goal = "lose"
        profile.save()
        self.assertTrue(profile.is_complete())


class TestLoginViewOriginal(TestCase):
    """Keep backward-compat with the original test structure."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="password123"
        )

    def test_login_view(self):
        response = self.client.get(reverse("account_login"))
        self.assertEqual(response.status_code, 200)

    def test_signup_view(self):
        response = self.client.get(reverse("account_signup"))
        self.assertEqual(response.status_code, 200)

    def test_profile_setup_view_authenticated(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.get(reverse("profile_setup"))
        self.assertEqual(response.status_code, 200)

    def test_profile_setup_view_unauthenticated(self):
        response = self.client.get(reverse("profile_setup"))
        self.assertRedirects(response, "/accounts/login/?next=/profile/setup/")
