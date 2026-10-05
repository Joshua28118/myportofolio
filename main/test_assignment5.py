from django.contrib.auth.models import Group, User
from django.test import Client, TestCase
from django.urls import reverse

from main.models import Experience


class Assignment5Tests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_superuser("assignment5_owner")
        cls.regular = User.objects.create_user("assignment5_regular", email="private@example.com")
        cls.editor = User.objects.create_user("assignment5_editor")
        cls.editor.groups.add(Group.objects.create(name="Editor"))
        cls.staff = User.objects.create_user("assignment5_staff", is_staff=True)

    def setUp(self):
        self.create_url = reverse("main:create_experience_ajax")
        self.api_url = reverse("main:get_experience_json")
        self.list_url = reverse("main:show_experience")
        self.payload = {
            "title": "Research Assistant", "description": "Research work",
            "category": "research", "thumbnail": "", "ended_at": "",
        }

    def login_as(self, user):
        self.client.logout()
        if user:
            self.client.force_login(user)

    def test_json_and_skeleton_are_public_for_every_role(self):
        item = Experience.objects.create(title="Private research title", description="Research work")
        for user in (None, self.regular, self.editor, self.staff, self.owner):
            self.login_as(user)
            with self.subTest(user=user):
                response = self.client.get(self.list_url)
                self.assertEqual(response.status_code, 200)
                self.assertNotContains(response, item.title)
                self.assertNotIn("experience_list", response.context)
                self.assertContains(response, 'id="grid"')
                self.assertContains(response, 'id="experience-card-template"')
                self.assertContains(response, "js/experience.js")
                data = self.client.get(self.api_url).json()
                self.assertEqual(data[0]["fields"]["title"], item.title)

    def test_modal_and_card_actions_follow_roles(self):
        for user in (None, self.regular, self.editor, self.staff, self.owner):
            self.login_as(user)
            response = self.client.get(self.list_url)
            for marker, allowed in (
                ('id="experience-form"', user == self.owner),
                ('class="experience-delete"', user == self.owner),
                ('class="button experience-edit"', user in (self.owner, self.editor)),
                ('class="star-form"', user is not None),
            ):
                with self.subTest(user=user, marker=marker):
                    (self.assertContains if allowed else self.assertNotContains)(response, marker)

    def test_ajax_create_allows_only_owner(self):
        for user in (None, self.regular, self.editor, self.staff):
            self.login_as(user)
            with self.subTest(user=user):
                response = self.client.post(self.create_url, self.payload)
                self.assertEqual(response.status_code, 403)
                self.assertIn("message", response.json())
                self.assertFalse(Experience.objects.exists())
        self.login_as(self.owner)
        response = self.client.post(self.create_url, self.payload)
        self.assertEqual(response.status_code, 201)
        item = Experience.objects.get()
        self.assertEqual(str(item.pk), response.json()["pk"])
        self.assertTrue(item.is_ongoing)
        self.assertFalse(item.starred_by.exists())

    def test_ajax_requires_post_for_anonymous_and_owner(self):
        for user in (None, self.owner):
            self.login_as(user)
            for method in ("get", "put", "patch", "delete"):
                with self.subTest(user=user, method=method):
                    self.assertEqual(getattr(self.client, method)(self.create_url).status_code, 405)
        self.assertFalse(Experience.objects.exists())

    def test_csrf_missing_and_invalid_tokens_are_rejected(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        client.get(self.list_url)
        self.assertEqual(client.post(self.create_url, self.payload).status_code, 403)
        self.assertEqual(client.post(self.create_url, self.payload, HTTP_X_CSRFTOKEN="bad").status_code, 403)
        self.assertFalse(Experience.objects.exists())
        response = client.post(
            self.create_url, self.payload, HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Experience.objects.count(), 1)

    def test_invalid_fields_return_json_errors_without_saving(self):
        self.login_as(self.owner)
        for field, value in (
            ("title", "   "), ("title", '<img src="x" onerror="alert(1)">'),
            ("title", "x" * 256), ("description", ""), ("description", "<p></p>"),
            ("category", "unknown"), ("thumbnail", "javascript:alert(1)"),
            ("thumbnail", "data:image/svg+xml,test"), ("ended_at", "not-a-date"),
        ):
            with self.subTest(field=field, value=value):
                response = self.client.post(self.create_url, {**self.payload, field: value})
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.json()["errors"])
                self.assertFalse(Experience.objects.exists())

    def test_cleaning_applies_to_ajax_create_and_existing_create_edit(self):
        dirty = {
            **self.payload, "title": " <b>Research</b> & Development ",
            "description": "<p>Research <em>work</em></p>",
        }
        self.login_as(self.owner)
        for url in (self.create_url, reverse("main:create_experience")):
            response = self.client.post(url, dirty)
            self.assertIn(response.status_code, (201, 302))
            item = Experience.objects.get()
            self.assertEqual(item.title, "Research & Development")
            self.assertEqual(item.description, "Research work")
            item.delete()
        item = Experience.objects.create(title="Before", description="Before")
        self.login_as(self.editor)
        self.assertEqual(self.client.post(reverse("main:edit_experience", args=[item.pk]), dirty).status_code, 302)
        item.refresh_from_db()
        self.assertEqual(item.title, "Research & Development")
        self.assertEqual(item.description, "Research work")

    def test_search_is_trimmed_case_insensitive_and_can_be_empty(self):
        first = Experience.objects.create(title="Research Assistant", description="One")
        second = Experience.objects.create(title="Volunteer", description="Two")
        data = self.client.get(self.api_url, {"title": "  RESEARCH  "}).json()
        self.assertEqual([item["pk"] for item in data], [str(first.pk)])
        self.assertEqual(self.client.get(self.api_url, {"title": "missing"}).json(), [])
        self.assertEqual(len(self.client.get(self.api_url, {"title": "  "}).json()), 2)
        self.assertEqual(self.client.get(self.list_url, {"title": " RESEARCH "}).context["title_query"], "RESEARCH")
        self.assertEqual(self.client.get(self.api_url).json()[0]["pk"], str(second.pk))
        Experience.objects.all().delete()
        self.assertEqual(self.client.get(self.api_url).json(), [])

    def test_json_contains_public_fields_and_session_specific_stars(self):
        item = Experience.objects.create(title="Research", description="Work", category="research")
        item.starred_by.add(self.regular, self.editor)
        for user, starred in ((None, False), (self.regular, True), (self.editor, True), (self.owner, False)):
            self.login_as(user)
            response = self.client.get(self.api_url)
            fields = response.json()[0]["fields"]
            self.assertEqual(set(fields), {
                "title", "description", "category", "category_display", "thumbnail",
                "started_at", "ended_at", "is_ongoing", "star_count", "is_starred",
            })
            self.assertEqual(fields["star_count"], 2)
            self.assertEqual(fields["is_starred"], starred)
            for private in ("starred_by", "password", "email", self.regular.username, self.regular.email):
                self.assertNotContains(response, private)

    def test_star_toggle_updates_json_and_detail(self):
        item = Experience.objects.create(title="Research", description="Work")
        self.login_as(self.regular)
        url = reverse("main:toggle_experience_star", args=[item.pk])
        for expected in (True, False):
            self.assertEqual(self.client.post(url).status_code, 302)
            fields = self.client.get(self.api_url).json()[0]["fields"]
            self.assertEqual(fields["is_starred"], expected)
            self.assertEqual(fields["star_count"], int(expected))
            response = self.client.get(reverse("main:experience_detail", args=[item.pk]))
            self.assertContains(response, f'aria-pressed="{str(expected).lower()}"')

    def test_completed_date_and_category_display(self):
        self.login_as(self.owner)
        response = self.client.post(self.create_url, {
            **self.payload, "category": "part-time", "ended_at": "2026-10-05T12:30",
        })
        self.assertEqual(response.status_code, 201)
        fields = self.client.get(self.api_url).json()[0]["fields"]
        self.assertFalse(fields["is_ongoing"])
        self.assertEqual(fields["category_display"], "Part-Time")
        self.assertTrue(fields["ended_at"].startswith("2026-10-05T12:30"))
        self.assertTrue(fields["started_at"])

    def test_extra_post_fields_cannot_control_stars_or_primary_key(self):
        self.login_as(self.owner)
        response = self.client.post(self.create_url, {
            **self.payload, "starred_by": [self.regular.pk],
            "id": "00000000-0000-0000-0000-000000000000", "is_superuser": "true",
        })
        self.assertEqual(response.status_code, 201)
        item = Experience.objects.get()
        self.assertNotEqual(str(item.pk), "00000000-0000-0000-0000-000000000000")
        self.assertFalse(item.starred_by.exists())

    def test_empty_form_reports_required_fields(self):
        self.login_as(self.owner)
        response = self.client.post(self.create_url, {})
        self.assertEqual(response.status_code, 400)
        self.assertTrue({"title", "description", "category"}.issubset(response.json()["errors"]))
        self.assertFalse(Experience.objects.exists())
