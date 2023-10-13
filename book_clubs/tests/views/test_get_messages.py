from django.test import TestCase
from django.urls import reverse
from book_clubs.models import Book, Club, Meeting, Message, User, Membership
from book_clubs.tests.helpers import LogInTester, reverse_with_next
from django.http import JsonResponse

class GetMessagesTestCase(TestCase, LogInTester):
    """Tests of the get messages view."""

    fixtures = [
        'book_clubs/tests/fixtures/multiple_memberships_and_meetings.json',
        'book_clubs/tests/fixtures/single_book.json'
    ]

    def setUp(self):
        self.user1 = User.objects.get(id = 1)
        self.user2 = User.objects.get(id = 2)
        self.club = Club.objects.get(id = 1)
        self.membership = Membership.objects.get(club = self.club, member = self.user1)
        self.meeting1 = Meeting.objects.get(id = 1, club = self.club)
        self.book = Book.objects.get(isbn = "0000000001")
        self.url = reverse('get_messages', kwargs = {'club_id' : 1, 'meeting_id' : 1})

    def test_get_message_url(self):
        self.assertEqual(self.url, '/get_messages/1/1/')

    def test_user_is_a_member_of_the_club_and_successfull_reception_of_messages(self):
        self.client.login(username = self.user1.username, password = 'Password123')
        self.assertTrue(self._is_logged_in())
        Meeting.objects.filter(id = self.meeting1.id).update(chosen_book = self.book)
        response = self.client.get(self.url, follow = True)
        self.assertEquals(response.status_code, 200)

    def test_user_is_not_a_member_of_the_club_and_unsuccessful_get_reception_of_messages(self):
        self.client.login(username = self.user2.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)
        response_url = reverse('user_club_list')
        self.assertRedirects(response, response_url, status_code = 302, target_status_code=200)

    def test_get_messages_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        response = self.client.get(self.url)
        response_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
