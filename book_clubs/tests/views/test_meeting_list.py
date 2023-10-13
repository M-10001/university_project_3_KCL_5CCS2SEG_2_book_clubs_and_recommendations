from book_clubs.models import User, Club, Membership, Meeting
from django.test import TestCase
from django.urls import reverse
from book_clubs.tests.helpers import LogInTester,reverse_with_next

class MeetingListTestCase(TestCase, LogInTester):
    """Tests of the meeting list view."""

    fixtures = ['book_clubs/tests/fixtures/multiple_memberships.json']

    def setUp(self):
        self.club1 = Club.objects.get(id = 1)
        self.membership1 = Membership.objects.get(id = 1)
        self.url = reverse('meeting_list', kwargs={'club_id': self.club1.id})

    def test_meeting_list_url(self):
        self.assertEqual(self.url, f'/meeting_list/1/')

    def test_get_meeting_list(self):
        self.client.login(username = 'test1', password = 'Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'meeting_list.html')
        self.assertEqual(len(response.context['meetings']), len(Meeting.objects.filter(club = self.membership1.club)))

    def test_get_meeting_list_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code = 302, target_status_code = 200)

    def test_get_meeting_list_when_invalid_club_id(self):
        self.client.login(username = 'test1', password = 'Password123')
        self.assertTrue(self._is_logged_in())
        self.url = reverse('meeting_list', kwargs={'club_id': 0})
        redirect_url = reverse('user_club_list')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code = 302, target_status_code = 200)

    def test_get_meeting_list_when_user_is_not_member(self):
        self.client.login(username = 'test1', password = 'Password123')
        self.assertTrue(self._is_logged_in())
        self.url = reverse('meeting_list', kwargs = {'club_id' : Club.objects.get(id = 2).id})
        redirect_url = reverse('user_club_list')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code = 302, target_status_code = 200)
