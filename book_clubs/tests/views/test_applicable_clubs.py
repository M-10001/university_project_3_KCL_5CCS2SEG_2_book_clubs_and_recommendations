from django.test import TestCase
from django.urls import reverse
from book_clubs.models import User, Club, Application, Membership
from book_clubs.tests.helpers import LogInTester, reverse_with_next

class ApplicableClubsViewTestCase(TestCase, LogInTester):

    fixtures = ['book_clubs/tests/fixtures/single_user.json']

    def setUp(self):
        self.url = reverse('applicable_clubs')
        self.user = User.objects.get(id = 1)

    def test_get_url(self):
        self.assertEqual(self.url, '/applicable_clubs/')

    def test_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        response = self.client.get(self.url)
        response_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, response_url, status_code = 302, target_status_code = 200)

    def test_get_applicable_clubs(self):
        self.client.login(username=self.user.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applicable_clubs.html')
        self.assertEqual(len(response.context['clubs']), len(Club.objects.exclude(applicants = self.user).exclude(members = self.user)))
