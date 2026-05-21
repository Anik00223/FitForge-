from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class AccountsViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", email="test@test.com", password="password123")

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
        self.assertRedirects(response, f"/accounts/login/?next=/profile/setup/")
