from django.test import TestCase
from django.urls import reverse
from book_clubs.models import User, Club, Application
from book_clubs.tests.helpers import LogInTester, reverse_with_next

class CreateUserApplicationListTestCase(TestCase, LogInTester):
    """Tests of the user application list view."""

    fixtures = [
        'book_clubs/tests/fixtures/multiple_applications.json'
        ]

    def setUp(self):
        self.url = reverse('user_application_list')
        self.user = User.objects.get(id = 1)

    def test_user_application_list_url(self):
        self.assertEqual(self.url, '/user_application_list/')

    def test_get_user_application_list_when_logged_in(self):
        self.client.login(username=self.user.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_application_list.html')
        self.assertEqual(len(response.context['applications']), len(Application.objects.filter(applicant = self.user)))

    def test_get_user_application_list_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        response = self.client.get(self.url)
        response_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
