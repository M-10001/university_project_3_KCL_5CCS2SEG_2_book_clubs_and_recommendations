from django.test import TestCase
from django.urls import reverse
from book_clubs.models import User, Club, Membership, Book, Meeting
from book_clubs.tests.helpers import LogInTester,reverse_with_next

class SelectMeetingBookTestCase(TestCase, LogInTester):
    """Select Meeting Book Tests"""

    fixtures = [
        'book_clubs/tests/fixtures/multiple_memberships_and_meetings_with_book_chooser.json',
        'book_clubs/tests/fixtures/single_book.json'
    ]

    def setUp(self):
        self.user1 = User.objects.get(id = 1)
        self.club1 = Club.objects.get(id = 1)
        self.club2 = Club.objects.get(id = 2)
        self.meeting1 = Meeting.objects.get(id = 1)
        self.meeting2 = Meeting.objects.get(id = 2)
        self.book1 = Book.objects.get(isbn = '0000000001')
        self.url = reverse('select_meeting_book', kwargs = {'club_id' : self.club1.id, 'meeting_id' : self.meeting1.id, 'book_isbn' : self.book1.isbn})

    def test_url(self):
        self.assertEqual(self.url, '/select_meeting_book/1/1/0000000001/')

    def test_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        response = self.client.get(self.url)
        response_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, response_url, status_code = 302, target_status_code = 200)

    def test_club_id_is_invalid(self):
        self.client.login(username=self.user1.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.url = reverse('select_meeting_book', kwargs = {'club_id' : 0, 'meeting_id' : self.meeting1.id, 'book_isbn' : self.book1.isbn})
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('user_club_list'), status_code=302, target_status_code=200)

    def test_user_is_not_member_of_club(self):
        self.client.login(username=self.user1.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.url = reverse('select_meeting_book', kwargs = {'club_id' : self.club2.id, 'meeting_id' : self.meeting1.id, 'book_isbn' : self.book1.isbn})
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('user_club_list'), status_code=302, target_status_code=200)

    def test_invalid_meeting_id(self):
        self.client.login(username=self.user1.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.url = reverse('select_meeting_book', kwargs = {'club_id' : self.club1.id, 'meeting_id' : 0, 'book_isbn' : self.book1.isbn})
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('club_page', kwargs = {'club_id' : self.club1.id}), status_code=302, target_status_code=200)

    def test_meeting_not_of_club(self):
        self.client.login(username=self.user1.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.url = reverse('select_meeting_book', kwargs = {'club_id' : self.club1.id, 'meeting_id' : self.meeting2.id, 'book_isbn' : self.book1.isbn})
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('club_page', kwargs = {'club_id' : self.club1.id}), status_code=302, target_status_code=200)

    def test_book_chooser_not_current_user(self):
        self.client.login(username=self.user1.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.meeting1.book_chooser = None
        self.meeting1.save()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('club_page', kwargs = {'club_id' : self.club1.id}), status_code=302, target_status_code=200)

    def test_meeting_not_active(self):
        self.client.login(username=self.user1.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.meeting1.active = False
        self.meeting1.save()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('club_page', kwargs = {'club_id' : self.club1.id}), status_code=302, target_status_code=200)

    def test_chosen_book_exists(self):
        self.client.login(username=self.user1.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.meeting1.chosen_book = self.book1
        self.meeting1.save()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('club_page', kwargs = {'club_id' : self.club1.id}), status_code=302, target_status_code=200)

    def test_book_isbn_is_invalid(self):
        self.client.login(username=self.user1.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.url = reverse('select_meeting_book', kwargs = {'club_id' : self.club1.id, 'meeting_id' : self.meeting1.id, 'book_isbn' : '0000000000'})
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('meeting_book_selection', kwargs = {'club_id' : self.club1.id, 'meeting_id' : self.meeting1.id, 'page' : 0}), status_code=302, target_status_code=200)
