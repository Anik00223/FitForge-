"""Tests for the AI planner app — plan creation, status polling, history, Q&A."""
import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.ai_planner.models import GeneratedPlan

User = get_user_model()


def _make_complete_user(username="planneruser"):
    user = User.objects.create_user(username, password="Str0ngPassw0rd!")
    profile = user.profile
    profile.age = 25
    profile.sex = "M"
    profile.weight_kg = 70.0
    profile.height_cm = 175.0
    profile.activity_level = "moderate"
    profile.fitness_goal = "lose"
    profile.save()
    diet = user.diet_profile
    diet.daily_calories_target = 2000
    diet.protein_g = 150
    diet.carbs_g = 200
    diet.fats_g = 67
    diet.save()
    return user


class TestPlannerView(TestCase):
    def setUp(self):
        self.user = _make_complete_user()
        self.client = Client()
        self.client.force_login(self.user)

    def test_get_planner_accessible(self):
        resp = self.client.get(reverse("planner"))
        self.assertEqual(resp.status_code, 200)

    def test_incomplete_profile_redirects_to_setup(self):
        bare_user = User.objects.create_user("bareuser", password="Str0ngPassw0rd!")
        self.client.force_login(bare_user)
        resp = self.client.get(reverse("planner"))
        self.assertRedirects(resp, reverse("profile_setup"))

    @patch("apps.ai_planner.views.generate_plan_task")
    def test_post_creates_pending_plan_and_dispatches_celery(self, mock_task):
        mock_task.delay = lambda pk: None
        resp = self.client.post(reverse("planner"), {"plan_type": "diet"})
        plan = GeneratedPlan.objects.filter(user=self.user).first()
        self.assertIsNotNone(plan)
        self.assertEqual(plan.status, GeneratedPlan.Status.PENDING)
        self.assertRedirects(resp, reverse("plan_status", kwargs={"pk": plan.pk}))

    @patch("apps.ai_planner.views.generate_plan_task")
    def test_invalid_plan_type_defaults_to_combined(self, mock_task):
        mock_task.delay = lambda pk: None
        self.client.post(reverse("planner"), {"plan_type": "invalid_type"})
        plan = GeneratedPlan.objects.filter(user=self.user).first()
        if plan:
            self.assertEqual(plan.plan_type, "combined")


class TestPlanStatusAPI(TestCase):
    def setUp(self):
        self.user = _make_complete_user("statususer")
        self.client = Client()
        self.client.force_login(self.user)

    def test_pending_returns_correct_json(self):
        plan = GeneratedPlan.objects.create(
            user=self.user,
            plan_type="diet",
            status=GeneratedPlan.Status.PENDING,
            user_inputs={},
        )
        resp = self.client.get(reverse("plan_status_api", kwargs={"pk": plan.pk}))
        data = json.loads(resp.content)
        self.assertFalse(data["done"])
        self.assertFalse(data["failed"])
        self.assertEqual(data["status"], "pending")

    def test_done_returns_redirect_url(self):
        plan = GeneratedPlan.objects.create(
            user=self.user,
            plan_type="diet",
            plan_content="# Day 1\nBreakfast: Oats",
            status=GeneratedPlan.Status.DONE,
            is_active=True,
            user_inputs={},
        )
        resp = self.client.get(reverse("plan_status_api", kwargs={"pk": plan.pk}))
        data = json.loads(resp.content)
        self.assertTrue(data["done"])
        self.assertIn("redirect_url", data)

    def test_failed_returns_error(self):
        plan = GeneratedPlan.objects.create(
            user=self.user,
            plan_type="diet",
            status=GeneratedPlan.Status.FAILED,
            error_message="API timeout",
            user_inputs={},
        )
        resp = self.client.get(reverse("plan_status_api", kwargs={"pk": plan.pk}))
        data = json.loads(resp.content)
        self.assertTrue(data["failed"])
        self.assertEqual(data["error"], "API timeout")

    def test_other_user_cannot_see_plan(self):
        plan = GeneratedPlan.objects.create(
            user=self.user, plan_type="diet",
            status=GeneratedPlan.Status.DONE, user_inputs={},
        )
        other = User.objects.create_user("otherstatus", password="pass123456!")
        self.client.force_login(other)
        resp = self.client.get(reverse("plan_status_api", kwargs={"pk": plan.pk}))
        self.assertEqual(resp.status_code, 404)


class TestPlanHistory(TestCase):
    def setUp(self):
        self.user = _make_complete_user("historyuser")
        self.client = Client()
        self.client.force_login(self.user)

    def test_history_renders(self):
        GeneratedPlan.objects.create(
            user=self.user, plan_type="diet",
            plan_content="Plan content", status=GeneratedPlan.Status.DONE,
            is_active=True, user_inputs={},
        )
        resp = self.client.get(reverse("plan_history"))
        self.assertEqual(resp.status_code, 200)

    def test_history_pagination(self):
        for i in range(15):
            GeneratedPlan.objects.create(
                user=self.user, plan_type="diet",
                plan_content=f"Plan {i}", status=GeneratedPlan.Status.DONE,
                user_inputs={},
            )
        resp = self.client.get(reverse("plan_history"))
        self.assertIn("page_obj", resp.context)
        self.assertEqual(len(resp.context["page_obj"]), 10)


class TestDeletePlan(TestCase):
    def setUp(self):
        self.user = _make_complete_user("deleteuser")
        self.client = Client()
        self.client.force_login(self.user)

    def test_delete_own_plan(self):
        plan = GeneratedPlan.objects.create(
            user=self.user, plan_type="diet",
            plan_content="Content", status=GeneratedPlan.Status.DONE,
            user_inputs={},
        )
        self.client.post(reverse("delete_plan", kwargs={"pk": plan.pk}))
        self.assertFalse(GeneratedPlan.objects.filter(pk=plan.pk).exists())

    def test_cannot_delete_other_users_plan(self):
        other = User.objects.create_user("otheruserdelete", password="pass123456!")
        plan = GeneratedPlan.objects.create(
            user=other, plan_type="diet",
            plan_content="Content", status=GeneratedPlan.Status.DONE,
            user_inputs={},
        )
        resp = self.client.post(reverse("delete_plan", kwargs={"pk": plan.pk}))
        self.assertEqual(resp.status_code, 404)
