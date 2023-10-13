from django.test import TestCase
from django.urls import reverse
from book_clubs.models import Book, Club, Meeting, MeetingRecommendation, User
from book_clubs.tests.helpers import LogInTester, reverse_with_next

class CreateMeetingBookSelectionTestCase(TestCase, LogInTester):
    """Tests for the meeting_book_selection view."""

    fixtures = [
        'book_clubs/tests/fixtures/multiple_memberships_and_meetings.json'
        ]

    def setUp(self):
        self.user1 = User.objects.get(id = 1)
        self.user2 = User.objects.get(id = 2)
        self.club = Club.objects.get(id = 1)
        self.not_club = Club.objects.get(id = 2)
        self.meeting = Meeting.objects.get(id = 1)
        self.not_meeting = Meeting.objects.get(id = 2)
        self.url = reverse('meeting_book_selection', kwargs={'club_id': self.club.id, 'meeting_id': self.meeting.id, 'page' : 0})

    def test_meeting_book_selection_url(self):
        self.assertEqual(self.url, '/meeting_book_selection/1/1/0/')

    def test_get_meeting_book_selection(self):
        self.client.login(username=self.user1.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        Meeting.objects.filter(id = 1).update(book_chooser = self.user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meeting_book_selection.html')

    def test_get_meeting_book_selection_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        response = self.client.get(self.url)
        response_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_get_meeting_book_selection_when_meeting_id_is_not_valid(self):
        self.client.login(username=self.user1.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        self.url = reverse('meeting_book_selection', kwargs={'club_id': self.club.id, 'meeting_id': 0, 'page' : 0})
        response = self.client.get(self.url)
        response_url = reverse('club_page', kwargs = {'club_id' : self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_get_meeting_book_selection_when_meeting_is_not_of_this_club(self):
        self.client.login(username=self.user1.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        url = reverse('meeting_book_selection', kwargs={'club_id': self.club.id, 'meeting_id': self.not_meeting.id, 'page' : 0})
        response = self.client.get(url)
        response_url = reverse('club_page', kwargs = {'club_id' : self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_get_meeting_book_selection_when_book_chooser_is_not_current_user(self):
        self.client.login(username=self.user1.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)
        response_url = reverse('club_page', kwargs = {'club_id' : self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_get_meeting_book_selection_when_meeting_is_not_active(self):
        self.client.login(username=self.user1.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        Meeting.objects.filter(id = 1).update(active = False)
        response = self.client.get(self.url)
        response_url = reverse('club_page', kwargs = {'club_id' : self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_get_meeting_book_selection_when_user_does_not_have_membership_to_club(self):
        self.client.login(username=self.user2.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)
        response_url = reverse('user_club_list')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_get_meeting_book_selection_when_club_id_is_not_valid(self):
        self.client.login(username=self.user2.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        self.url = reverse('meeting_book_selection', kwargs={'club_id': 0, 'meeting_id': self.meeting.id, 'page' : 0})
        response = self.client.get(self.url)
        response_url = reverse('user_club_list')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
