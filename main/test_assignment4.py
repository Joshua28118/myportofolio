from datetime import date
from uuid import uuid4

from django.contrib.auth.models import Group, User
from django.test import Client, TestCase
from django.urls import reverse

from main.models import Education, Experience, Project


class Assignment4Tests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = "Assignment4-Test-Password!"
        cls.regular = User.objects.create_user("regular", password=cls.password)
        cls.editor = User.objects.create_user("editor", password=cls.password)
        cls.staff = User.objects.create_user("staff", is_staff=True)
        cls.owner = User.objects.create_superuser("owner", password=cls.password)
        cls.group = Group.objects.create(name="Editor")
        cls.editor.groups.add(cls.group)

    def setUp(self):
        self.experience = Experience.objects.create(
            title="Volunteer", description="Help organize events", category="volunteer"
        )
        self.project = Project.objects.create(
            title="Portfolio", description="Website", tech_stack="Django"
        )
        self.education = Education.objects.create(
            institution="UI", program="Computer Science", description="Study",
            started_at=date(2025, 8, 1),
        )
        self.sections = [
            ("experience", Experience, self.experience, {
                "title": "Updated experience", "description": "New description",
                "category": "research", "thumbnail": "", "ended_at": "",
            }),
            ("project", Project, self.project, {
                "title": "Updated project", "description": "New description",
                "tech_stack": "Python", "project_url": "",
            }),
            ("education", Education, self.education, {
                "institution": "Updated institution", "program": "CS",
                "description": "New description", "started_at": "2025-08-01",
                "ended_at": "",
            }),
        ]

    def login_as(self, user):
        self.client.logout()
        if user is not None:
            self.client.force_login(user)

    def test_public_pages_and_json_for_every_role(self):
        urls = [reverse("main:" + name) for name in (
            "show_main", "show_experience", "show_projects", "show_education",
            "get_experience_json", "get_projects_json", "get_education_json",
        )]
        urls.append(reverse("main:experience_detail", args=[self.experience.pk]))
        for user in (None, self.regular, self.editor, self.owner):
            self.login_as(user)
            for url in urls:
                with self.subTest(user=user, url=url):
                    self.assertEqual(self.client.get(url).status_code, 200)

    def test_anonymous_mutations_redirect_without_changing_data(self):
        for section, model, item, payload in self.sections:
            original = model.objects.get(pk=item.pk).__dict__.copy()
            for action in ("create", "edit", "delete"):
                url = reverse(f"main:{action}_{section}", args=[] if action == "create" else [item.pk])
                for method in ("get", "post"):
                    with self.subTest(section=section, action=action, method=method):
                        response = getattr(self.client, method)(url, payload if method == "post" else {})
                        self.assertRedirects(response, reverse("main:login") + "?next=" + url,
                                             fetch_redirect_response=False)
                        self.assertEqual(model.objects.count(), 1)
            current = model.objects.get(pk=item.pk)
            self.assertEqual(current.description, original["description"])

    def test_regular_and_staff_cannot_mutate_any_section(self):
        for user in (self.regular, self.staff):
            self.login_as(user)
            for section, model, item, payload in self.sections:
                for action in ("create", "edit", "delete"):
                    url = reverse(f"main:{action}_{section}", args=[] if action == "create" else [item.pk])
                    for method in ("get", "post"):
                        with self.subTest(user=user, section=section, action=action, method=method):
                            self.assertEqual(getattr(self.client, method)(url, payload).status_code, 403)
                self.assertEqual(model.objects.count(), 1)
                item.refresh_from_db()
                self.assertNotEqual(item.description, payload["description"])

    def test_editor_can_update_but_cannot_create_or_delete(self):
        self.login_as(self.editor)
        for section, model, item, payload in self.sections:
            with self.subTest(section=section):
                edit = reverse(f"main:edit_{section}", args=[item.pk])
                self.assertEqual(self.client.get(edit).status_code, 200)
                self.assertEqual(self.client.post(edit, payload).status_code, 302)
                item.refresh_from_db()
                self.assertEqual(item.description, payload["description"])
                for action in ("create", "delete"):
                    url = reverse(f"main:{action}_{section}", args=[] if action == "create" else [item.pk])
                    self.assertEqual(self.client.get(url).status_code, 403)
                    self.assertEqual(self.client.post(url, payload).status_code, 403)
                self.assertEqual(model.objects.count(), 1)

    def test_owner_can_create_update_and_delete(self):
        self.login_as(self.owner)
        for section, model, item, payload in self.sections:
            with self.subTest(section=section):
                self.assertEqual(self.client.post(reverse(f"main:create_{section}"), payload).status_code, 302)
                self.assertEqual(model.objects.count(), 2)
                self.assertEqual(self.client.post(reverse(f"main:edit_{section}", args=[item.pk]), payload).status_code, 302)
                item.refresh_from_db()
                self.assertEqual(item.description, payload["description"])
                delete = reverse(f"main:delete_{section}", args=[item.pk])
                self.assertEqual(self.client.get(delete).status_code, 405)
                self.assertEqual(self.client.post(delete).status_code, 302)
                self.assertFalse(model.objects.filter(pk=item.pk).exists())
                self.assertEqual(model.objects.count(), 1)

    def test_action_controls_match_permissions(self):
        for user in (None, self.regular, self.staff, self.editor, self.owner):
            self.login_as(user)
            for section, _, item, _ in self.sections:
                list_name = "show_projects" if section == "project" else f"show_{section}"
                response = self.client.get(reverse("main:" + list_name))
                for action in ("create", "edit", "delete"):
                    url = reverse(f"main:{action}_{section}", args=[] if action == "create" else [item.pk])
                    allowed = user == self.owner or (user == self.editor and action == "edit")
                    with self.subTest(user=user, section=section, action=action):
                        if allowed:
                            self.assertContains(response, url)
                        else:
                            self.assertNotContains(response, url)

    def test_detail_controls_and_missing_item(self):
        url = reverse("main:experience_detail", args=[self.experience.pk])
        for user in (None, self.regular, self.editor, self.owner):
            self.login_as(user)
            response = self.client.get(url)
            self.assertContains(response, self.experience.title)
            self.assertContains(response, self.experience.description)
            edit = reverse("main:edit_experience", args=[self.experience.pk])
            delete = reverse("main:delete_experience", args=[self.experience.pk])
            (self.assertContains if user in (self.editor, self.owner) else self.assertNotContains)(response, edit)
            (self.assertContains if user == self.owner else self.assertNotContains)(response, delete)
        self.assertEqual(self.client.get(reverse("main:experience_detail", args=[uuid4()])).status_code, 404)

    def test_editor_group_removal_takes_effect(self):
        self.login_as(self.editor)
        self.editor.groups.remove(self.group)
        url = reverse("main:edit_experience", args=[self.experience.pk])
        self.assertEqual(self.client.get(url).status_code, 403)

    def test_star_toggle_for_all_authenticated_roles_and_multiple_users(self):
        for item, route, page in (
            (self.experience, "toggle_experience_star", "show_experience"),
            (self.project, "toggle_star", "show_projects"),
        ):
            url = reverse("main:" + route, args=[item.pk])
            for user in (self.regular, self.editor, self.owner):
                self.login_as(user)
                with self.subTest(item=item, user=user):
                    self.assertEqual(self.client.post(url).status_code, 302)
                    self.assertEqual(item.starred_by.count(), 1)
                    response = self.client.get(reverse("main:" + page))
                    self.assertContains(response, 'aria-pressed="true"')
                    self.assertContains(response, '<span class="star-count">1</span>', html=True)
                    item.starred_by.add(user)
                    self.assertEqual(item.starred_by.count(), 1)
                    self.assertEqual(self.client.post(url).status_code, 302)
                    self.assertEqual(item.starred_by.count(), 0)
                    self.assertContains(self.client.get(reverse("main:" + page)), 'aria-pressed="false"')
            item.starred_by.add(self.regular, self.editor)
            self.login_as(self.regular)
            self.client.post(url)
            self.assertEqual(list(item.starred_by.all()), [self.editor])

    def test_star_requires_login_and_post(self):
        for item, route in ((self.experience, "toggle_experience_star"), (self.project, "toggle_star")):
            url = reverse("main:" + route, args=[item.pk])
            self.login_as(None)
            self.assertEqual(self.client.post(url).status_code, 302)
            self.login_as(self.regular)
            for method in ("get", "put", "delete"):
                self.assertEqual(getattr(self.client, method)(url).status_code, 405)
            self.assertEqual(item.starred_by.count(), 0)

    def test_star_csrf_rejects_missing_token_and_accepts_valid_token(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.regular)
        client.get(reverse("main:show_experience"))
        token = client.cookies["csrftoken"].value
        for item, route in ((self.experience, "toggle_experience_star"), (self.project, "toggle_star")):
            url = reverse("main:" + route, args=[item.pk])
            self.assertEqual(client.post(url).status_code, 403)
            self.assertEqual(item.starred_by.count(), 0)
            self.assertEqual(client.post(url, {"csrfmiddlewaretoken": token}).status_code, 302)
            self.assertEqual(item.starred_by.count(), 1)

    def test_star_from_detail_returns_to_detail_and_missing_item_is_404(self):
        self.login_as(self.regular)
        url = reverse("main:toggle_experience_star", args=[self.experience.pk])
        response = self.client.post(url, {"return_to": "detail"})
        self.assertRedirects(response, reverse("main:experience_detail", args=[self.experience.pk]))
        self.assertContains(self.client.get(response.url), 'aria-pressed="true"')
        for route in ("toggle_experience_star", "toggle_star"):
            self.assertEqual(self.client.post(reverse("main:" + route, args=[uuid4()])).status_code, 404)

    def test_json_excludes_user_relations_and_private_data(self):
        self.regular.email = "private-email@example.com"
        self.regular.save()
        self.experience.starred_by.add(self.regular)
        self.project.starred_by.add(self.regular)
        for route, expected_fields in (
            ("get_experience_json", {"title", "description", "category", "thumbnail", "started_at", "ended_at"}),
            ("get_projects_json", {"title", "description", "tech_stack", "project_url"}),
        ):
            response = self.client.get(reverse("main:" + route))
            self.assertEqual(set(response.json()[0]["fields"]), expected_fields)
            for private in ("starred_by", self.regular.email, self.regular.password):
                self.assertNotContains(response, private)

    def test_public_star_display_does_not_expose_usernames(self):
        self.experience.starred_by.add(self.regular)
        self.project.starred_by.add(self.regular)
        for route in ("show_experience", "show_projects"):
            response = self.client.get(reverse("main:" + route))
            self.assertContains(response, "1 star")
            self.assertContains(response, "Login untuk memberi star")
            self.assertNotContains(response, self.regular.username)

    def test_registration_cannot_self_assign_editor_or_superuser(self):
        response = self.client.post(reverse("main:register"), {
            "username": "newuser", "password1": self.password, "password2": self.password,
            "groups": [self.group.pk], "is_superuser": "on", "is_staff": "on",
        })
        self.assertRedirects(response, reverse("main:login"))
        user = User.objects.get(username="newuser")
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.groups.exists())

    def test_login_session_cookie_and_logout(self):
        response = self.client.post(reverse("main:login"), {
            "username": self.regular.username, "password": self.password,
        })
        self.assertRedirects(response, reverse("main:show_main"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.regular.pk)
        self.assertTrue(response.cookies["last_login"].value)
        response = self.client.get(reverse("main:logout"))
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertEqual(response.cookies["last_login"]["max-age"], 0)

    def test_login_honors_safe_next_and_rejects_external_redirect(self):
        for destination, expected in (
            ("/experience/", "/experience/"),
            ("https://untrusted.example/", "/"),
            ("//untrusted.example/", "/"),
        ):
            self.client.logout()
            response = self.client.post(reverse("main:login"), {
                "username": self.regular.username, "password": self.password,
                "next": destination,
            })
            self.assertRedirects(response, expected)
        response = self.client.get(reverse("main:login"), {"next": "/experience/"})
        self.assertContains(response, 'name="next" value="/experience/"')

    def test_nonstaff_editor_cannot_manage_groups_in_admin(self):
        self.login_as(self.editor)
        response = self.client.get(reverse("admin:auth_group_changelist"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("admin:login"), response.url)
