from django.contrib.auth.models import Group, User
from django.test import Client, TestCase
from django.urls import reverse

from main.forms import ProjectForm
from main.models import Project


class Tutorial5Tests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_superuser("owner5")
        cls.regular = User.objects.create_user("regular5", email="private@example.com")
        cls.editor = User.objects.create_user("editor5")
        cls.editor.groups.add(Group.objects.create(name="Editor"))
        cls.staff = User.objects.create_user("staff5", is_staff=True)

    def setUp(self):
        self.url = reverse("main:create_project_ajax")
        self.payload = {
            "title": "Portfolio", "description": "My website",
            "tech_stack": "Django", "project_url": "https://example.com/",
        }

    def test_only_owner_can_create_via_ajax(self):
        for user in (None, self.regular, self.editor, self.staff):
            self.client.logout()
            if user:
                self.client.force_login(user)
            with self.subTest(user=user):
                response = self.client.post(self.url, self.payload)
                self.assertEqual(response.status_code, 403)
                self.assertIn("message", response.json())
                self.assertFalse(Project.objects.exists())
        self.client.force_login(self.owner)
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(str(Project.objects.get().pk), response.json()["pk"])

    def test_ajax_requires_post(self):
        for user in (None, self.owner):
            if user:
                self.client.force_login(user)
            for method in ("get", "put", "patch", "delete"):
                with self.subTest(user=user, method=method):
                    self.assertEqual(getattr(self.client, method)(self.url).status_code, 405)
        self.assertFalse(Project.objects.exists())

    def test_ajax_rejects_invalid_input_without_saving(self):
        self.client.force_login(self.owner)
        for field, value in (
            ("title", "   "), ("title", '<img src="x" onerror="alert(1)">'),
            ("title", "x" * 256), ("description", ""),
            ("tech_stack", ""), ("project_url", "javascript:alert(1)"),
            ("project_url", "data:text/html,test"),
        ):
            with self.subTest(field=field, value=value):
                response = self.client.post(self.url, {**self.payload, field: value})
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.json()["errors"])
                self.assertFalse(Project.objects.exists())

    def test_csrf_required_and_header_accepted(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        client.get(reverse("main:show_projects"))
        self.assertEqual(client.post(self.url, self.payload).status_code, 403)
        self.assertFalse(Project.objects.exists())
        response = client.post(
            self.url, self.payload, HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Project.objects.count(), 1)

    def test_cleaning_applies_to_ajax_and_existing_create_and_edit(self):
        dirty = {
            **self.payload, "title": " Hello <b>world</b> ",
            "description": "<p>Website</p>", "tech_stack": "<em>Django</em>",
        }
        self.client.force_login(self.owner)
        for url in (self.url, reverse("main:create_project")):
            self.client.post(url, dirty)
            item = Project.objects.get(title="Hello world")
            self.assertEqual(item.description, "Website")
            self.assertEqual(item.tech_stack, "Django")
            item.delete()
        item = Project.objects.create(**self.payload)
        self.client.force_login(self.editor)
        response = self.client.post(reverse("main:edit_project", args=[item.pk]), dirty)
        self.assertEqual(response.status_code, 302)
        item.refresh_from_db()
        self.assertEqual(item.title, "Hello world")

    def test_optional_url_and_literal_special_characters(self):
        form = ProjectForm({**self.payload, "title": 'A & B "quoted"', "project_url": ""})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.save().title, 'A & B "quoted"')

    def test_json_star_state_is_session_specific_and_private_data_is_absent(self):
        item = Project.objects.create(**self.payload)
        item.starred_by.add(self.regular)
        for user, starred in ((None, False), (self.regular, True), (self.editor, False)):
            self.client.logout()
            if user:
                self.client.force_login(user)
            response = self.client.get(reverse("main:get_projects_json"))
            fields = response.json()[0]["fields"]
            self.assertEqual(fields["star_count"], 1)
            self.assertEqual(fields["is_starred"], starred)
            for private in (self.regular.username, self.regular.email, "password", "starred_by"):
                self.assertNotContains(response, private)

    def test_page_is_a_skeleton_and_modal_is_owner_only(self):
        Project.objects.create(**self.payload)
        for user in (None, self.regular, self.editor, self.owner):
            self.client.logout()
            if user:
                self.client.force_login(user)
            response = self.client.get(reverse("main:show_projects"))
            self.assertNotIn("project_list", response.context)
            self.assertContains(response, 'id="grid"')
            self.assertContains(response, 'id="toast-component"')
            self.assertContains(response, "js/projects.js")
            assertion = self.assertContains if user == self.owner else self.assertNotContains
            assertion(response, 'id="project-form"')
            assertion(response, 'class="project-delete"')
            assertion = self.assertContains if user in (self.editor, self.owner) else self.assertNotContains
            assertion(response, 'class="button project-edit"')
