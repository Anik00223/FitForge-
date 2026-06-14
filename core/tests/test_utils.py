"""Tests for core utilities — BMI calculation, TDEE, macros, streak."""
from django.test import TestCase

from core.utils import (
    calculate_bmi,
    calculate_macros,
    calculate_tdee,
    get_bmi_badge_class,
    get_workout_streak,
)


class TestCalculateBMI(TestCase):
    def test_normal_weight(self):
        bmi, category = calculate_bmi(70, 175)
        self.assertAlmostEqual(bmi, 22.9, places=0)
        self.assertEqual(category, "Normal Weight")

    def test_underweight(self):
        bmi, category = calculate_bmi(45, 175)
        self.assertEqual(category, "Underweight")

    def test_overweight(self):
        bmi, category = calculate_bmi(90, 175)
        self.assertEqual(category, "Overweight")

    def test_obese(self):
        bmi, category = calculate_bmi(120, 175)
        self.assertEqual(category, "Obese")

    def test_zero_height_returns_none(self):
        self.assertIsNone(calculate_bmi(70, 0))

    def test_zero_weight_returns_none(self):
        self.assertIsNone(calculate_bmi(0, 175))


class TestCalculateTDEE(TestCase):
    def test_male_sedentary(self):
        tdee = calculate_tdee(70, 175, 25, "M", "sedentary")
        self.assertGreater(tdee, 1500)
        self.assertLess(tdee, 2500)

    def test_female_active(self):
        tdee = calculate_tdee(60, 165, 30, "F", "very")
        self.assertGreater(tdee, 2000)

    def test_unknown_activity_defaults_sedentary(self):
        tdee_known = calculate_tdee(70, 175, 25, "M", "sedentary")
        tdee_unknown = calculate_tdee(70, 175, 25, "M", "unknown_level")
        self.assertEqual(tdee_known, tdee_unknown)


class TestCalculateMacros(TestCase):
    def test_lose_weight_macros(self):
        macros = calculate_macros(2000, "lose")
        self.assertIn("protein_g", macros)
        self.assertIn("carbs_g", macros)
        self.assertIn("fats_g", macros)

    def test_gain_muscle_macros(self):
        macros = calculate_macros(2500, "gain")
        # Gain has highest carb ratio (0.50)
        self.assertGreater(macros["carbs_g"], macros["protein_g"])

    def test_unknown_goal_defaults_to_maintain(self):
        macros_maintain = calculate_macros(2000, "maintain")
        macros_unknown = calculate_macros(2000, "unknown_goal")
        self.assertEqual(macros_maintain, macros_unknown)


class TestGetBMIBadgeClass(TestCase):
    def test_known_categories(self):
        self.assertEqual(get_bmi_badge_class("Underweight"), "badge-info")
        self.assertEqual(get_bmi_badge_class("Normal Weight"), "badge-success")
        self.assertEqual(get_bmi_badge_class("Overweight"), "badge-warning")
        self.assertEqual(get_bmi_badge_class("Obese"), "badge-danger")

    def test_unknown_category(self):
        self.assertEqual(get_bmi_badge_class("Alien"), "badge-secondary")
