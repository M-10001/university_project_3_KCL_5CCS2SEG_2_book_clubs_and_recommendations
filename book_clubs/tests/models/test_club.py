from django.test import TestCase
from django.core.exceptions import ValidationError
from book_clubs.models import Club

class ClubModelTestCase(TestCase):

    fixtures = ['book_clubs/tests/fixtures/multiple_clubs.json']

    def setUp(self):
        self.club1 = Club.objects.get(id = 1)
        self.club2 = Club.objects.get(id = 2)

    def test_valid_club(self):
        self._assert_club_is_valid(self.club1)

    def test_name_must_not_be_blank(self):
        self.club1.name = ''
        self._assert_club_is_invalid(self.club1)

    def test_name_may_be_not_unique(self):
        self.club1.name = self.club2.name
        self._assert_club_is_valid(self.club1)

    def test_name_must_not_be_greater_than_50_characters(self):
        self.club1.name = 'a' * 51
        self._assert_club_is_invalid(self.club1)

    def test_description_can_be_blank(self):
        self.club1.description = ''
        self._assert_club_is_valid(self.club1)

    def test_description_may_be_not_unique(self):
        self.club1.description = self.club2.description
        self._assert_club_is_valid(self.club1)

    def test_description_must_not_be_greater_than_1000_characters(self):
        self.club1.description = 'a' * 1001
        self._assert_club_is_invalid(self.club1)

    def test_str_returns_name(self):
        self.assertTrue(self.club1.__str__() == self.club1.name)

    def test_meeting_cycle_must_not_be_lower_than_default(self):
        self.club1.meeting_cycle = Club.MEETING_CYCLE_DEFAULT - 1
        self._assert_club_is_invalid(self.club1)

    def test_meeting_cycle_must_not_be_greater_than_or_equal_to_total_member_plus_default_while_greater_than_default(self):
        self.club1.meeting_cycle = self.club1.members.count() + Club.MEETING_CYCLE_DEFAULT + 1
        self._assert_club_is_invalid(self.club1)

    def test_meeting_cycle_must_not_be_assigned_greater_than_default_upon_creation(self):
        self.club1.delete()
        self.club1 = Club(name = self.club1.name, description = self.club1.description, meeting_cycle = Club.MEETING_CYCLE_DEFAULT + 1)
        self._assert_club_is_invalid(self.club1)

    def _assert_club_is_valid(self, club):
        try:
            club.full_clean()
        except (ValidationError):
            self.fail('Test club should be valid.')

    def _assert_club_is_invalid(self, club):
        with self.assertRaises(ValidationError):
            club.full_clean()
