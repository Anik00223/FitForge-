from django.test import TestCase
from django.contrib.auth.models import User
from apps.accounts.models import UserProfile
from apps.nutrition.models import DietProfile

class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@test.com", password="password123")
    
    def test_profile_auto_created(self):
        # The post_save signal should automatically create a UserProfile and DietProfile
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())
        self.assertTrue(DietProfile.objects.filter(user=self.user).exists())
    
    def test_profile_str(self):
        profile = self.user.profile
        self.assertEqual(str(profile), "testuser profile")

    def test_is_complete_false(self):
        profile = self.user.profile
        self.assertFalse(profile.is_complete())
        
    def test_is_complete_true(self):
        profile = self.user.profile
        profile.age = 25
        profile.sex = "M"
        profile.weight_kg = 75.0
        profile.height_cm = 180.0
        profile.activity_level = "moderate"
        profile.fitness_goal = "gain"
        self.assertTrue(profile.is_complete())
