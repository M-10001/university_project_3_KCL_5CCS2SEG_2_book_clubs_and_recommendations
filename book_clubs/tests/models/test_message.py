from django.test import TestCase
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import IntegrityError
from book_clubs.models import Book, Club, Meeting, Membership, Message, User

class MessageModelTestCase(TestCase):
    '''Tests for the Message model.'''

    fixtures = ['book_clubs/tests/fixtures/multiple_memberships_and_meetings.json']

    def setUp(self):
        self.user1 = User.objects.get(id = 1)
        self.user2 = User.objects.get(id = 2)
        self.club = Club.objects.get(id = 1)
        self.membership = Membership.objects.get(club = self.club, member = self.user1)
        self.meeting1 = Meeting.objects.get(id = 1)
        self.message = Message.objects.create(
            value = 'This is a test.',
            post_time = '2000-01-01T00:00:10+00:00',
            name_of_user = self.user1.username,
            meeting = self.meeting1
        )

    def test_valid_message(self):
        self._assert_message_is_valid(self.message)

    def test_message_can_be_a_million_characters_long(self):
        message = Message.objects.create(
            value = 'X' * 1000000,
            post_time = '2000-01-01T00:00:20+00:00',
            name_of_user = self.user1.username,
            meeting = self.meeting1
        )
        self._assert_message_is_valid(message)

    def test_message_cannot_be_over_million_characters_long(self):
        message = Message.objects.create(
            value = 'X' * 1000001,
            post_time = '2000-01-01T00:00:30+00:00',
            name_of_user = self.user1.username,
            meeting = self.meeting1
        )
        self._assert_message_is_invalid(message)

    def test_message_cannot_be_blank(self):
        try:
            message = Message.objects.create(
                value = None,
                post_time = '2000-01-01T00:00:40+00:00',
                name_of_user = self.user1.username,
                meeting = self.meeting1
            )
        except IntegrityError:
            pass

    def test_users_not_a_part_of_a_club_cannot_send_a_message_in_a_meeting(self):
        try:
            membership = Membership.objects.get(club = self.club, member = self.user2)
            message = Message.objects.create(
                value = 'This is another test.',
                post_time = '2000-01-01T00:00:40+00:00',
                name_of_user = self.user2.username,
                meeting = self.meeting1
            )
        except:
            pass

    def _assert_message_is_valid(self, message):
        try:
            message.full_clean()
        except (ValidationError, ObjectDoesNotExist, IntegrityError):
            self.fail('Test message should be valid.')

    def _assert_message_is_invalid(self, message):
        try:
            message.full_clean()
        except (ValidationError, ObjectDoesNotExist, IntegrityError):
            pass
