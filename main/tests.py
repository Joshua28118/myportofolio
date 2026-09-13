from datetime import date

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Experience, Education


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="PBP Teaching Assistant",
            description="Help students understand web development.",
            category="part-time",
        )

        self.education = Education.objects.create(
            institution="Universitas Indonesia",
            program="Ilmu Komputer",
            description="Undergraduate student at the Faculty of Computer Science, Universitas Indonesia.",
            started_at=date(2025, 8, 1),
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)

        self.assertContains(
            response,
            f'href="{reverse("main:show_experience")}"'
        )

        self.assertContains(
            response,
            f'href="{reverse("main:show_education")}"'
        )

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/a-page-that-does-not-exist/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(
            str(self.experience),
            "PBP Teaching Assistant"
        )

        self.assertEqual(
            self.experience.category,
            "part-time"
        )

        self.assertTrue(
            self.experience.is_ongoing
        )

    def test_experience_page(self):
        response = self.client.get(
            reverse("main:show_experience")
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")

        self.assertContains(
            response,
            self.experience.title
        )

        self.assertContains(
            response,
            self.experience.description
        )

        self.assertContains(
            response,
            "Part-Time"
        )

        self.assertContains(
            response,
            "Ongoing"
        )

        self.assertContains(
            response,
            f'href="{reverse("main:show_main")}"'
        )

    def test_empty_experience_page(self):
        Experience.objects.all().delete()

        response = self.client.get(
            reverse("main:show_experience")
        )

        self.assertContains(
            response,
            "No experience has been added yet."
        )

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()

        response = self.client.get(
            reverse("main:show_experience")
        )

        self.assertFalse(
            self.experience.is_ongoing
        )

        self.assertContains(
            response,
            "Completed"
        )

        self.assertNotContains(
            response,
            "Ongoing"
        )

    def test_education_url_is_accessible_and_uses_correct_template(self):
        response = self.client.get(
            reverse("main:show_education")
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education.html")

    def test_education_data_appears_in_html(self):
        response = self.client.get(
            reverse("main:show_education")
        )

        self.assertContains(
            response,
            "Universitas Indonesia"
        )

        self.assertContains(
            response,
            "Ilmu Komputer"
        )

        self.assertContains(
            response,
            "Undergraduate student at the Faculty of Computer Science, Universitas Indonesia."
        )

        self.assertContains(
            response,
            "Present"
        )

    def test_empty_education_page(self):
        Education.objects.all().delete()

        response = self.client.get(
            reverse("main:show_education")
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            "No education has been added yet."
        )