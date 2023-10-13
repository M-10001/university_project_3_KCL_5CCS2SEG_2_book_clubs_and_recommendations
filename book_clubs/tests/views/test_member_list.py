from book_clubs.models import User, Club, Membership
from django.test import TestCase
from django.urls import reverse
from book_clubs.tests.helpers import LogInTester,reverse_with_next

class MemberListTestCase(TestCase, LogInTester):
    """Tests of the member list view."""

    fixtures = ['book_clubs/tests/fixtures/single_membership.json']

    def setUp(self):
        self.url = reverse('member_list', kwargs={'club_id': 1})
        self.membership1 = Membership.objects.get(id = 1)

    def test_member_list_url(self):
        self.assertEqual(self.url, f'/member_list/1/')

    def test_get_member_list(self):
        self.client.login(username = 'test1', password = 'Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'member_list.html')
        self.assertEqual(len(response.context['membership_list']), len(Membership.objects.filter(club = self.membership1.club)))

    def test_get_member_list_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code = 302, target_status_code = 200)

    def test_get_member_list_when_invalid_club_id(self):
        self.client.login(username = 'test1', password = 'Password123')
        self.assertTrue(self._is_logged_in())
        self.url = reverse('member_list', kwargs={'club_id': 0})
        redirect_url = reverse('user_club_list')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code = 302, target_status_code = 200)

    def test_get_member_list_when_user_is_not_member(self):
        self.client.login(username = 'test1', password = 'Password123')
        self.assertTrue(self._is_logged_in())
        self.membership1.delete()
        redirect_url = reverse('user_club_list')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code = 302, target_status_code = 200)
