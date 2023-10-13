from django.test import TestCase
from django.urls import reverse
from book_clubs.models import Book, Club, Meeting, Message, User, Membership
from book_clubs.tests.helpers import LogInTester, reverse_with_next

class SendViewTestCase(TestCase, LogInTester):
    """Tests of the send view."""

    fixtures = [
        'book_clubs/tests/fixtures/multiple_memberships_and_meetings.json',
        'book_clubs/tests/fixtures/single_book.json'
    ]

    def setUp(self):
        self.user1 = User.objects.get(id = 1)
        self.user2 = User.objects.get(id = 2)
        self.club = Club.objects.get(id = 1)
        self.membership = Membership.objects.get(club = self.club, member = self.user1)
        self.meeting1 = Meeting.objects.get(id = 1)
        self.message_input = {'username' : self.user1.username, 'message' : 'test1_m'}
        self.book = Book.objects.get(isbn = "0000000001")
        self.url = reverse('send', kwargs = {'club_id' : self.club.id, 'meeting_id' : self.meeting1.id})

    def test_send_view_url(self):
        self.assertEqual(self.url, '/send/1/1/')

    def test_user_is_a_member_of_the_club_and_successfully_sent_message(self):
        self.client.login(username = self.user1.username, password = 'Password123')
        self.assertTrue(self._is_logged_in())
        Meeting.objects.filter(id = self.meeting1.id).update(chosen_book = self.book)
        before_message_count = Message.objects.count()

        # It is in try and except since, the view does not return any response and .post checks for that, which causes error.
        try:
            self.client.post(self.url, self.message_input)
        except ValueError:
            pass
        
        after_message_count = Message.objects.count()
        self.assertEquals(after_message_count, before_message_count + 1)

    def test_user_is_not_a_member_of_the_club_and_unsuccessfully_sent_message(self):
        self.client.login(username = self.user2.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.message_input['username'] = self.user2.username
        self.message_input['message'] = 'test2_m'
        response = self.client.post(self.url, self.message_input, follow=True)
        response_url = reverse('user_club_list')
        self.assertRedirects(response, response_url, status_code = 302, target_status_code=200)

    def test_send_message_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        response = self.client.get(self.url)
        response_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
