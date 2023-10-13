from django.utils import timezone
from django.test import TestCase
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from book_clubs.models import User, Club, Membership, Book, Meeting

class MeetingModelTestCase(TestCase):

    fixtures = [
        'book_clubs/tests/fixtures/multiple_memberships_and_meetings.json',
        'book_clubs/tests/fixtures/single_book.json'
    ]

    def setUp(self):
        self.user1 = User.objects.get(id = 1)
        self.user2 = User.objects.get(id = 2)
        self.club1 = Club.objects.get(id = 1)
        self.club2 = Club.objects.get(id = 2)
        self.book1 = Book.objects.get(isbn = '0000000001')
        self.meeting1 = Meeting.objects.get(id = 1)
        self.meeting2 = Meeting.objects.get(id = 2)

    def test_valid_meeting(self):
        self._assert_meeting_is_valid(self.meeting1)

    def test_club_must_not_be_None(self):
        self.meeting1.club = None
        self._assert_meeting_is_invalid(self.meeting1)

    def test_club_may_not_be_unique(self):
        self.meeting1.club = self.meeting2.club
        self._assert_meeting_is_valid(self.meeting1)

    def test_book_chooser_may_not_be_unique(self):
        self.meeting1.book_chooser = self.user1
        self.meeting2.book_chooser = self.meeting1.book_chooser
        Membership.objects.create(club = self.club2, member = self.user1, member_type = Membership.MemberTypes.MEMBER)
        self.meeting2.save()
        self._assert_meeting_is_valid(self.meeting1)

    def test_book_chooser_must_be_member_of_club(self):
        self.meeting1.book_chooser = self.user2
        self._assert_meeting_is_invalid(self.meeting1)

    def test_chosen_book_may_not_be_unique(self):
        self.meeting1.chosen_book = self.book1
        self.meeting2.chosen_book = self.book1
        self.meeting2.save()
        self._assert_meeting_is_valid(self.meeting1)

    def test_deadline_must_not_be_set_to_before_now_on_creation(self):
        self.meeting1.delete()
        self.meeting1.deadline = timezone.now()
        self.meeting1.deadline = self.meeting1.deadline.replace(year = timezone.now().year - 1)

        try:
            Meeting.objects.create(
                club = self.meeting1.club,
                book_chooser = None,
                chosen_book = None,
                active = True,
                deadline = self.meeting1.deadline
            )
        except (ValidationError):
            pass

    def test_deadline_must_not_be_set_to_before_now(self):
        self.meeting1.deadline = timezone.now()
        self.meeting1.deadline = self.meeting1.deadline.replace(year = timezone.now().year - 1)
        self._assert_meeting_is_invalid(self.meeting1)

    def _assert_meeting_is_valid(self, meeting):
        try:
            meeting.full_clean()
        except (ValidationError, ObjectDoesNotExist):
            self.fail('Test meeting should be valid.')

    def _assert_meeting_is_invalid(self, meeting):
        try:
            meeting.full_clean()
        except (ValidationError, ObjectDoesNotExist):
            pass
