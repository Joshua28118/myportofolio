from django.test import TestCase
from django.urls import reverse

from .models import Contact


class ContactPageTest(TestCase):
    def setUp(self):
        self.ani = Contact.objects.create(name="Ani", email="ani@example.com")
        self.budi = Contact.objects.create(name="Budi", email="budi@example.com")

    def test_list_page_renders_all_contacts(self):
        response = self.client.get(reverse("contacts:contact_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="contact-rows"')
        self.assertContains(response, "Ani")
        self.assertContains(response, "Budi")

    def test_list_page_loads_htmx_and_csrf_header(self):
        response = self.client.get(reverse("contacts:contact_list"))
        self.assertContains(response, "htmx.min.js")
        self.assertContains(response, "X-CSRFToken")


class ContactAddTest(TestCase):
    def test_add_creates_contact_and_returns_rows_fragment(self):
        response = self.client.post(
            reverse("contacts:contact_add"),
            {"name": "Ani", "email": "ani@example.com"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Contact.objects.filter(name="Ani").exists())
        body = response.content.decode()
        self.assertIn("<tr", body)
        self.assertNotIn("<html", body)

    def test_add_rejects_get(self):
        response = self.client.get(reverse("contacts:contact_add"))
        self.assertEqual(response.status_code, 405)


class ContactSearchTest(TestCase):
    def setUp(self):
        Contact.objects.create(name="Ani", email="ani@example.com")
        Contact.objects.create(name="Budi", email="budi@example.com")

    def test_search_filters_case_insensitively(self):
        response = self.client.get(reverse("contacts:contact_search"), {"q": "an"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ani")
        self.assertNotContains(response, "Budi")

    def test_empty_query_returns_all_contacts(self):
        response = self.client.get(reverse("contacts:contact_search"), {"q": ""})
        self.assertContains(response, "Ani")
        self.assertContains(response, "Budi")

    def test_no_match_renders_empty_state(self):
        response = self.client.get(reverse("contacts:contact_search"), {"q": "zzz"})
        self.assertContains(response, "No contacts.")


class ContactEditTest(TestCase):
    def setUp(self):
        self.contact = Contact.objects.create(name="Ani", email="ani@example.com")

    def test_edit_returns_form_row(self):
        response = self.client.get(
            reverse("contacts:contact_edit", args=[self.contact.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'form="edit-form-{self.contact.pk}"')
        self.assertContains(response, "Save")
        self.assertContains(response, "Cancel")

    def test_cancel_returns_display_row(self):
        response = self.client.get(
            reverse("contacts:contact_row", args=[self.contact.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'id="contact-{self.contact.pk}"')
        self.assertNotContains(response, "<input")

    def test_update_saves_changes_and_returns_display_row(self):
        response = self.client.put(
            reverse("contacts:contact_update", args=[self.contact.pk]),
            "name=Ani+Revisi&email=revisi%40example.com",
            content_type="application/x-www-form-urlencoded",
        )
        self.assertEqual(response.status_code, 200)
        self.contact.refresh_from_db()
        self.assertEqual(self.contact.name, "Ani Revisi")
        self.assertEqual(self.contact.email, "revisi@example.com")
        self.assertContains(response, "Ani Revisi")
        self.assertNotContains(response, "<input")

    def test_update_rejects_post(self):
        response = self.client.post(
            reverse("contacts:contact_update", args=[self.contact.pk]), {}
        )
        self.assertEqual(response.status_code, 405)

    def test_update_returns_404_for_unknown_contact(self):
        response = self.client.put(
            reverse("contacts:contact_update", args=[9999]),
            "name=X&email=x%40example.com",
            content_type="application/x-www-form-urlencoded",
        )
        self.assertEqual(response.status_code, 404)


class ContactDeleteTest(TestCase):
    def setUp(self):
        self.contact = Contact.objects.create(name="Ani", email="ani@example.com")

    def test_delete_removes_contact_and_returns_empty_200(self):
        response = self.client.delete(
            reverse("contacts:contact_delete", args=[self.contact.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"")
        self.assertFalse(Contact.objects.filter(pk=self.contact.pk).exists())

    def test_delete_rejects_get(self):
        response = self.client.get(
            reverse("contacts:contact_delete", args=[self.contact.pk])
        )
        self.assertEqual(response.status_code, 405)


class ContactCsrfTest(TestCase):
    def test_add_without_csrf_token_is_rejected(self):
        client = self.client_class(enforce_csrf_checks=True)
        response = client.post(
            reverse("contacts:contact_add"),
            {"name": "Ani", "email": "ani@example.com"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Contact.objects.exists())
