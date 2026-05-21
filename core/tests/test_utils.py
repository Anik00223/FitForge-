from django.test import TestCase
from core.utils import calculate_bmi, calculate_tdee, calculate_macros, get_bmi_badge_class


class CalculateBMITest(TestCase):
    def test_normal_bmi(self):
        result = calculate_bmi(75, 180)
        self.assertIsNotNone(result)
        bmi, category = result
        self.assertEqual(bmi, 23.1)
        self.assertEqual(category, "Normal Weight")

    def test_underweight_bmi(self):
        bmi, category = calculate_bmi(50, 180)
        self.assertEqual(category, "Underweight")

    def test_overweight_bmi(self):
        bmi, category = calculate_bmi(85, 175)
        self.assertEqual(category, "Overweight")

    def test_obese_bmi(self):
        bmi, category = calculate_bmi(110, 170)
        self.assertEqual(category, "Obese")

    def test_zero_height_returns_none(self):
        self.assertIsNone(calculate_bmi(75, 0))

    def test_zero_weight_returns_none(self):
        self.assertIsNone(calculate_bmi(0, 180))

    def test_none_inputs_returns_none(self):
        self.assertIsNone(calculate_bmi(None, 180))
        self.assertIsNone(calculate_bmi(75, None))


class CalculateTDEETest(TestCase):
    def test_male_moderate(self):
        tdee = calculate_tdee(75, 180, 25, "M", "moderate")
        self.assertIsNotNone(tdee)
        self.assertGreater(tdee, 2000)

    def test_female_sedentary(self):
        tdee = calculate_tdee(60, 165, 30, "F", "sedentary")
        self.assertIsNotNone(tdee)
        self.assertGreater(tdee, 1200)

    def test_unknown_activity_defaults_sedentary(self):
        tdee_sedentary = calculate_tdee(75, 180, 25, "M", "sedentary")
        tdee_unknown = calculate_tdee(75, 180, 25, "M", "unknown_level")
        self.assertEqual(tdee_sedentary, tdee_unknown)


class CalculateMacrosTest(TestCase):
    def test_gain_macros(self):
        macros = calculate_macros(2500, "gain")
        self.assertIn("protein_g", macros)
        self.assertIn("carbs_g", macros)
        self.assertIn("fats_g", macros)
        # gain ratio: protein 0.30, carbs 0.50, fats 0.20
        self.assertEqual(macros["protein_g"], round((2500 * 0.30) / 4))
        self.assertEqual(macros["carbs_g"], round((2500 * 0.50) / 4))
        self.assertEqual(macros["fats_g"], round((2500 * 0.20) / 9))

    def test_lose_macros(self):
        macros = calculate_macros(2000, "lose")
        self.assertEqual(macros["protein_g"], round((2000 * 0.30) / 4))

    def test_maintain_macros(self):
        macros = calculate_macros(2200, "maintain")
        self.assertEqual(macros["protein_g"], round((2200 * 0.25) / 4))

    def test_endurance_macros(self):
        macros = calculate_macros(2800, "endurance")
        self.assertEqual(macros["carbs_g"], round((2800 * 0.60) / 4))

    def test_unknown_goal_defaults_to_maintain(self):
        macros_maintain = calculate_macros(2500, "maintain")
        macros_unknown = calculate_macros(2500, "nonexistent_goal")
        self.assertEqual(macros_maintain, macros_unknown)


class BMIBadgeClassTest(TestCase):
    def test_underweight(self):
        self.assertEqual(get_bmi_badge_class("Underweight"), "badge-info")

    def test_normal_weight(self):
        self.assertEqual(get_bmi_badge_class("Normal Weight"), "badge-success")

    def test_overweight(self):
        self.assertEqual(get_bmi_badge_class("Overweight"), "badge-warning")

    def test_obese(self):
        self.assertEqual(get_bmi_badge_class("Obese"), "badge-danger")

    def test_unknown_category(self):
        self.assertEqual(get_bmi_badge_class("Unknown"), "badge-secondary")

    def test_empty_string(self):
        self.assertEqual(get_bmi_badge_class(""), "badge-secondary")
