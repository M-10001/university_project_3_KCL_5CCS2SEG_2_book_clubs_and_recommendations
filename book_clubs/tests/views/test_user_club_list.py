from django.test import TestCase
from django.urls import reverse
from book_clubs.models import User
from book_clubs.tests.helpers import LogInTester, reverse_with_next

class UserClubListTestCase(TestCase, LogInTester):
    """User club list tests."""

    fixtures = ['book_clubs/tests/fixtures/single_membership.json']

    def setUp(self):
        self.url = reverse('user_club_list')
        self.user = User.objects.get(id = 1)

    def test_user_page_url(self):
        self.assertEqual(self.url,'/user_club_list/')

    def test_get_user_club_list_when_logged_in(self):
        self.client.login(username = 'test1', password = 'Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_club_list.html')
        clubs = response.context['clubs']
        self.assertEqual(len(clubs), self.user.memberships.count())

    def test_get_user_club_list_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        response = self.client.get(self.url)
        response_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
