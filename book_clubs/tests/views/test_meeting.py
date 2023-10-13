from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
from book_clubs.models import Book, Club, Meeting, Message, User, Membership
from book_clubs.tests.helpers import LogInTester, reverse_with_next
from django.http import JsonResponse

class MeetingTestCase(TestCase, LogInTester):
    """Tests of the get meeting view."""

    fixtures = [
        'book_clubs/tests/fixtures/multiple_memberships_and_meetings.json',
        'book_clubs/tests/fixtures/multiple_books.json'
    ]

    def setUp(self):
        self.user1 = User.objects.get(id = 1)
        self.user2 = User.objects.get(id = 2)
        self.club1 = Club.objects.get(id = 1)
        self.membership1 = Membership.objects.get(id = 1)
        self.meeting1 = Meeting.objects.get(id = 1)
        self.meeting2 = Meeting.objects.get(id = 2)
        self.book1 = Book.objects.get(isbn = '0000000001')
        self.url = reverse('meeting', kwargs = {'club_id' : 1, 'meeting_id' : 1})

    def test_meeting(self):
        self.assertEqual(self.url, '/meeting/1/1/')

    def test_get_meeting(self):
        self.client.login(username = self.user1.username, password = 'Password123')
        self.assertTrue(self._is_logged_in())
        Meeting.objects.filter(id = self.meeting1.id).update(chosen_book = self.book1)
        response = self.client.get(self.url, follow = True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'meeting.html')

    def test_user_is_not_a_member_of_the_club_and_cannot_enter_meeting(self):
        self.client.login(username = self.user2.username, password = 'Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)
        response_url = reverse('user_club_list')
        self.assertRedirects(response, response_url, status_code = 302, target_status_code=200)

    def test_user_is_redirected_to_log_in_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        response = self.client.get(self.url)
        response_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_redirect_to_meeting_list_view_if_meeting_is_not_of_club(self):
        self.client.login(username = self.user1.username, password = 'Password123')
        self.assertTrue(self._is_logged_in())
        url = reverse('meeting', kwargs = {'club_id' : self.club1.id, 'meeting_id' : self.meeting2.id})
        response = self.client.get(url, follow = True)
        response_url = reverse('meeting_list', kwargs = {'club_id' : self.club1.id})
        self.assertRedirects(response, response_url, status_code = 302, target_status_code=200)

    def test_redirect_to_meeting_list_view_if_meeting_is_not_active(self):
        self.client.login(username = self.user1.username, password = 'Password123')
        self.assertTrue(self._is_logged_in())
        setattr(self.meeting1, 'active', False)
        response = self.client.get(self.url, follow = True)
        response_url = reverse('meeting_list', kwargs = {'club_id' : self.club1.id})
        self.assertRedirects(response, response_url, status_code = 302, target_status_code=200)

    def test_redirect_to_meeting_list_view_if_meeting_deadline_is_not_crossed(self):
        self.client.login(username = self.user1.username, password = 'Password123')
        self.assertTrue(self._is_logged_in())
        self.meeting1.deadline = timezone.now()
        self.meeting1.deadline = self.meeting1.deadline.replace(year = timezone.now().year + 1)
        self.meeting1.save()
        response = self.client.get(self.url, follow = True)
        response_url = reverse('meeting_list', kwargs = {'club_id' : self.club1.id})
        self.assertRedirects(response, response_url, status_code = 302, target_status_code=200)

    def test_redirect_to_meeting_list_view_if_book_is_not_selected_for_meeting(self):
        self.client.login(username = self.user1.username, password = 'Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow = True)
        response_url = reverse('meeting_list', kwargs = {'club_id' : self.club1.id})
        self.assertRedirects(response, response_url, status_code = 302, target_status_code=200)

    def test_redirect_to_user_club_list_view_if_invalid_club_id(self):
        self.client.login(username = self.user1.username, password = 'Password123')
        self.assertTrue(self._is_logged_in())
        url = reverse('meeting', kwargs = {'club_id' : 0, 'meeting_id' : self.meeting1.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_club_list')
        self.assertRedirects(response, response_url, status_code = 302, target_status_code=200)
