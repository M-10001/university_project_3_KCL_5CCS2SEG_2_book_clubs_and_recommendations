from django.test import TestCase
from django.urls import reverse
from book_clubs.models import User
from book_clubs.tests.helpers import LogInTester, reverse_with_next

class UserPageTestCase(TestCase, LogInTester):
    """User Page Tests"""

    fixtures = ['book_clubs/tests/fixtures/single_user.json']

    def setUp(self):
        self.url = reverse('user_page')

    def test_get_user_page_when_logged_in(self):
        self.client.login(username = 'test1', password = 'Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_page.html')

    def test_get_user_page_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        response = self.client.get(self.url)
        response_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
