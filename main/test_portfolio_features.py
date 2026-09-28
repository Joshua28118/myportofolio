from uuid import uuid4

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from main.models import Experience, Project


class ExperienceFeatureTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_superuser(username='experience_owner')

    def setUp(self):
        self.client.force_login(self.owner)
        self.item = Experience.objects.create(
            title='Committee member', description='Event preparation', category='volunteer'
        )
        self.add_url = reverse('main:create_experience')
        self.edit_url = reverse('main:edit_experience', args=[self.item.pk])
        self.delete_url = reverse('main:delete_experience', args=[self.item.pk])
        self.payload = {
            'title': 'Research Assistant', 'description': 'Research work',
            'category': 'research', 'thumbnail': '', 'ended_at': '',
        }

    def test_list_exposes_actions_and_existing_status(self):
        response = self.client.get(reverse('main:show_experience'))
        self.assertContains(response, self.add_url)
        self.assertContains(response, self.edit_url)
        self.assertContains(response, self.delete_url)
        self.assertContains(response, 'Ongoing')
        self.assertContains(response, 'popover="auto"')

    def test_form_get_and_cancel(self):
        response = self.client.get(self.add_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertContains(response, reverse('main:show_experience'))

    def test_create_and_success_message(self):
        response = self.client.post(self.add_url, self.payload, follow=True)
        self.assertContains(response, 'Research Assistant')
        self.assertContains(response, 'Experience berhasil ditambahkan.')
        self.assertEqual(Experience.objects.count(), 2)

    def test_invalid_create_does_not_save(self):
        response = self.client.post(self.add_url, {**self.payload, 'category': 'invalid'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('category', response.context['form'].errors)
        self.assertEqual(Experience.objects.count(), 1)

    def test_edit_prefills_existing_values(self):
        response = self.client.get(self.edit_url)
        self.assertContains(response, 'Committee member')
        self.assertEqual(response.context['form'].instance.pk, self.item.pk)

    def test_edit_updates_same_object_and_completion_status(self):
        started_at = self.item.started_at
        response = self.client.post(self.edit_url, {**self.payload, 'ended_at': '2026-09-16T12:30'}, follow=True)
        self.item.refresh_from_db()
        self.assertEqual(Experience.objects.count(), 1)
        self.assertEqual(self.item.started_at, started_at)
        self.assertEqual(self.item.title, 'Research Assistant')
        self.assertFalse(self.item.is_ongoing)
        self.assertContains(response, 'Completed')

    def test_invalid_edit_preserves_original(self):
        response = self.client.post(self.edit_url, {**self.payload, 'title': ''})
        self.item.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)
        self.assertEqual(self.item.title, 'Committee member')

    def test_delete_get_cannot_remove_data(self):
        self.assertEqual(self.client.get(self.delete_url).status_code, 405)
        self.assertTrue(Experience.objects.filter(pk=self.item.pk).exists())

    def test_delete_post_removes_only_selected_record(self):
        other = Experience.objects.create(title='Other', description='Keep this')
        response = self.client.post(self.delete_url, follow=True)
        self.assertContains(response, 'Experience berhasil dihapus.')
        self.assertFalse(Experience.objects.filter(pk=self.item.pk).exists())
        self.assertTrue(Experience.objects.filter(pk=other.pk).exists())

    def test_missing_edit_and_delete_return_404(self):
        pk = uuid4()
        self.assertEqual(self.client.get(reverse('main:edit_experience', args=[pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse('main:delete_experience', args=[pk])).status_code, 404)

    def test_mutations_require_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        for url in [self.add_url, self.edit_url, self.delete_url]:
            with self.subTest(url=url):
                self.assertEqual(client.post(url, self.payload).status_code, 403)
        self.item.refresh_from_db()
        self.assertEqual(self.item.title, 'Committee member')


class ProjectFeatureTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_superuser(username='project_owner')

    def setUp(self):
        self.item = Project.objects.create(
            title='Portfolio Website', description='Personal site', tech_stack='Django, Python',
            project_url='https://example.com/portfolio',
        )
        self.list_url = reverse('main:show_projects')
        self.api_url = reverse('main:get_projects_json')
        self.add_url = reverse('main:create_project')
        self.delete_url = reverse('main:delete_project', args=[self.item.pk])
        self.payload = {'title': 'Weather App', 'description': 'Forecasts', 'tech_stack': 'Python', 'project_url': ''}

    def test_projects_navigation_keeps_education(self):
        for route in ['main:show_main', 'main:show_experience', 'main:show_education']:
            response = self.client.get(reverse(route))
            self.assertContains(response, f'href="{self.list_url}"')
            self.assertContains(response, f'href="{reverse("main:show_education")}"')

    def test_list_shows_content_link_and_delete(self):
        self.client.force_login(self.owner)
        response = self.client.get(self.list_url)
        self.assertTemplateUsed(response, 'projects.html')
        for text in ['Portfolio Website', 'Personal site', 'Django, Python', self.item.project_url, self.delete_url]:
            self.assertContains(response, text)

    def test_search_is_case_insensitive_and_trims_whitespace(self):
        Project.objects.create(**self.payload)
        response = self.client.get(self.list_url, {'title': '  PORTFOLIO  '})
        self.assertContains(response, 'Portfolio Website')
        self.assertNotContains(response, 'Weather App')
        self.assertContains(response, 'Reset')

    def test_empty_database_and_no_matches_have_different_messages(self):
        response = self.client.get(self.list_url, {'title': 'missing'})
        self.assertContains(response, 'Tidak ada proyek dengan nama')
        Project.objects.all().delete()
        self.assertContains(self.client.get(self.list_url), 'Belum ada proyek yang ditambahkan.')

    def test_json_contains_filtered_records(self):
        Project.objects.create(**self.payload)
        response = self.client.get(self.api_url, {'title': 'portfolio'})
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['pk'], str(self.item.pk))
        self.assertEqual(data[0]['fields']['title'], 'Portfolio Website')

    def test_create_form_and_save_without_optional_link(self):
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(self.add_url).status_code, 200)
        response = self.client.post(self.add_url, self.payload, follow=True)
        self.assertContains(response, 'Weather App')
        self.assertContains(response, 'Proyek berhasil ditambahkan.')
        self.assertEqual(Project.objects.count(), 2)

    def test_invalid_link_and_missing_required_fields_are_rejected(self):
        self.client.force_login(self.owner)
        for payload in [{}, {**self.payload, 'project_url': 'javascript:alert(1)'}]:
            response = self.client.post(self.add_url, payload)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context['form'].errors)
        self.assertEqual(Project.objects.count(), 1)

    def test_absent_link_is_not_rendered(self):
        self.item.project_url = ''
        self.item.save()
        self.assertNotContains(self.client.get(self.list_url), 'Lihat Proyek')

    def test_delete_get_preserves_and_post_removes_selected_project(self):
        self.client.force_login(self.owner)
        other = Project.objects.create(**self.payload)
        self.assertEqual(self.client.get(self.delete_url).status_code, 405)
        self.assertTrue(Project.objects.filter(pk=self.item.pk).exists())
        response = self.client.post(self.delete_url, follow=True)
        self.assertContains(response, 'Proyek berhasil dihapus.')
        self.assertFalse(Project.objects.filter(pk=self.item.pk).exists())
        self.assertTrue(Project.objects.filter(pk=other.pk).exists())

    def test_missing_delete_returns_404(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse('main:delete_project', args=[uuid4()]))
        self.assertEqual(response.status_code, 404)

    def test_mutations_require_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        self.assertEqual(client.post(self.add_url, self.payload).status_code, 403)
        self.assertEqual(client.post(self.delete_url).status_code, 403)
        self.assertTrue(Project.objects.filter(pk=self.item.pk).exists())

    def test_html_escapes_user_content(self):
        self.item.title = '<script>alert(1)</script>'
        self.item.save()
        response = self.client.get(self.list_url)
        self.assertNotContains(response, '<script>')
        self.assertContains(response, '&lt;script&gt;')
