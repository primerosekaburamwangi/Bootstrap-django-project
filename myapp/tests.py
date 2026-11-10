import re

from django.core import mail
from django.contrib.staticfiles.finders import find
from django.test import TestCase, override_settings


class HomePageTests(TestCase):
    def test_homepage_renders_and_static_assets_exist(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<title>Primo | Digital Studio</title>")
        self.assertContains(response, '<h1 class="sitename">Primo</h1>')
        self.assertNotContains(response, "Orbit | Digital Studio")
        self.assertContains(response, "We bring strategy, design, and technology together")

        html = response.content.decode()
        self.assertNotRegex(
            html,
            r"Lorem ipsum|Pellentesque|Vestibulum|Necessitatibus|Voluptatem|"
            r"Nemo enim|Praesent commodo|Cras mattis|Donec ullamcorper|Maecenas|"
            r"Aenean|Vivamus|Curabitur|Etiam rhoncus|Sed ut perspiciatis|"
            r"Excepteur sint|Duis aute|Nam libero|Temporibus autem|Itaque earum|"
            r"Ut enim ad minima|Quis nostrud|Nullam quis",
        )
        self.assertNotRegex(html, r'href="[^"]+\.html')
        static_paths = re.findall(r'(?:href|src)="/static/([^"]+)"', html)
        self.assertTrue(static_paths)
        for static_path in static_paths:
            with self.subTest(static_path=static_path):
                self.assertIsNotNone(find(static_path))

        self.assertContains(response, 'name="csrfmiddlewaretoken"')


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    EMAIL_HOST="smtp.example.com",
    DEFAULT_FROM_EMAIL="website@example.com",
    CONTACT_EMAIL="contact@example.com",
    NEWSLETTER_EMAIL="newsletter@example.com",
)
class FormSubmissionTests(TestCase):
    def test_contact_form_sends_email(self):
        response = self.client.post(
            "/forms/contact/",
            {
                "name": "Jane Doe",
                "email": "jane@example.com",
                "subject": "Project inquiry",
                "message": "Please contact me.",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["contact@example.com"])
        self.assertEqual(mail.outbox[0].reply_to, ["jane@example.com"])

    def test_newsletter_form_sends_email(self):
        response = self.client.post(
            "/forms/newsletter/",
            {"email": "jane@example.com"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")
        self.assertEqual(mail.outbox[0].to, ["newsletter@example.com"])

    def test_invalid_form_is_rejected(self):
        response = self.client.post(
            "/forms/contact/",
            {"name": "Jane", "email": "not-an-email"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(mail.outbox, [])


@override_settings(EMAIL_HOST="", CONTACT_EMAIL="", DEFAULT_FROM_EMAIL="")
class EmailConfigurationTests(TestCase):
    def test_contact_form_reports_missing_email_configuration(self):
        response = self.client.post(
            "/forms/contact/",
            {
                "name": "Jane Doe",
                "email": "jane@example.com",
                "subject": "Project inquiry",
                "message": "Please contact me.",
            },
        )

        self.assertEqual(response.status_code, 503)
        self.assertContains(
            response,
            "Email delivery is not configured on this site.",
            status_code=503,
        )
