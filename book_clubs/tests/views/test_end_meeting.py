from django.test import TestCase
from django.urls import reverse
from book_clubs.models import User, Club, Membership, Meeting
from book_clubs.tests.helpers import LogInTester, reverse_with_next

class EndMeetingTestCase(TestCase, LogInTester):
    """Select Meeting Book Tests"""

    fixtures = ['book_clubs/tests/fixtures/multiple_memberships_and_meetings.json',]

    def setUp(self):
        self.user1 = User.objects.get(id = 1)
        self.club1 = Club.objects.get(id = 1)
        self.club2 = Club.objects.get(id = 2)
        self.membership1 = Membership.objects.get(id = 1)
        self.meeting1 = Meeting.objects.get(id = 1)
        self.meeting2 = Meeting.objects.get(id = 2)
        self.url = reverse('end_meeting', kwargs = {'club_id' : self.club1.id, 'meeting_id' : self.meeting1.id})

    def test_url(self):
        self.assertEqual(self.url, '/end_meeting/1/1/')

    def test_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        response = self.client.get(self.url)
        response_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, response_url, status_code = 302, target_status_code = 200)

    def test_club_id_is_invalid(self):
        self.client.login(username=self.user1.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.url = reverse('end_meeting', kwargs = {'club_id' : 0, 'meeting_id' : self.meeting1.id})
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('user_club_list'), status_code=302, target_status_code=200)

    def test_user_is_not_member_of_club(self):
        self.client.login(username=self.user1.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.url = reverse('end_meeting', kwargs = {'club_id' : self.club2.id, 'meeting_id' : self.meeting1.id})
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('user_club_list'), status_code=302, target_status_code=200)

    def test_user_is_not_owner_of_club(self):
        self.client.login(username = self.user1.username, password = 'Password123')
        self.assertTrue(self._is_logged_in())
        self.membership1.member_type = Membership.MemberTypes.MEMBER
        self.membership1.save()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('meeting_list', kwargs = {'club_id' : self.club1.id}), status_code=302, target_status_code=200)

    def test_invalid_meeting_id(self):
        self.client.login(username=self.user1.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.url = reverse('end_meeting', kwargs = {'club_id' : self.club1.id, 'meeting_id' : 0})
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('meeting_list', kwargs = {'club_id' : self.club1.id}), status_code=302, target_status_code=200)

    def test_meeting_not_of_club(self):
        self.client.login(username=self.user1.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.url = reverse('end_meeting', kwargs = {'club_id' : self.club1.id, 'meeting_id' : self.meeting2.id})
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('meeting_list', kwargs = {'club_id' : self.club1.id}), status_code=302, target_status_code=200)

    def test_successful_end_meeting(self):
        self.client.login(username = self.user1.username, password = 'Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)
        self.assertFalse(Meeting.objects.get(id = self.meeting1.id).active)
