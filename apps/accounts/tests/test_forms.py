from django.test import TestCase
from django.contrib.auth.models import User
from apps.accounts.forms import SignupForm, LoginForm, ProfileSetupForm

class SignupFormTest(TestCase):
    def test_valid_signup(self):
        data = {
            "name": "Test User",
            "email": "test@test.com",
            "password": "password123",
            "confirm_password": "password123",
        }
        form = SignupForm(data=data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")
        
    def test_passwords_mismatch(self):
        data = {
            "name": "Test User",
            "email": "test@test.com",
            "password": "password123",
            "confirm_password": "password456",
        }
        form = SignupForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("confirm_password", form.errors)

class LoginFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test@test.com", email="test@test.com", password="password123")
        
    def test_valid_login(self):
        form = LoginForm(data={"email": "test@test.com", "password": "password123"})
        self.assertTrue(form.is_valid())
        
    def test_invalid_login(self):
        form = LoginForm(data={"email": "test@test.com", "password": "wrong"})
        self.assertFalse(form.is_valid())
