from django.test import TestCase
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from book_clubs.models import User, Club, Membership, Application

class MembershipModelTestCase(TestCase):

    fixtures = ['book_clubs/tests/fixtures/multiple_memberships.json']

    def setUp(self):
        self.user1 = User.objects.get(id = 1)
        self.club1 = Club.objects.get(id = 1)
        self.membership1 = Membership.objects.get(id = 1)

        self.user2 = User.objects.get(id = 2)
        self.club2 = Club.objects.get(id = 2)
        self.membership2 = Membership.objects.get(id = 2)

    def test_valid_membership(self):
        self._assert_membership_is_valid(self.membership1)

    def test_club_must_not_be_empty(self):
        self.membership1.club = None
        self._assert_membership_is_invalid(self.membership1)

    def test_club_may_not_be_unique(self):
        self.membership1.club = self.membership2.club
        self._assert_membership_is_valid(self.membership1)

    def test_member_must_not_be_empty(self):
        self.membership1.member = None
        self._assert_membership_is_invalid(self.membership1)

    def test_member_may_not_be_unique(self):
        self.membership1.member = self.membership2.member
        self._assert_membership_is_valid(self.membership1)

    def test_club_and_member_together_must_be_unique(self):
        self.membership1.club = self.membership2.club
        self.membership1.member = self.membership2.member
        self._assert_membership_is_invalid(self.membership1)

    def test_must_not_create_membership_with_same_club_and_user_as_existing_application(self):
        self.membership1.delete()
        Application.objects.create(club = self.club1, applicant = self.user1)
        self.membership1 = Membership(club = self.club1, member = self.user1, member_type = 1)
        self._assert_membership_is_invalid(self.membership1)

    def test_member_type_must_not_be_different_from_choices(self):
        self.membership1.member_type = 2
        self._assert_membership_is_invalid(self.membership1)

    def test_is_member(self):
        self.assertFalse(self.membership1.is_member())
        self.membership1.member_type = Membership.MemberTypes.MEMBER
        self.assertTrue(self.membership1.is_member())

    def test_is_owner(self):
        self.assertTrue(self.membership1.is_owner())
        self.membership1.member_type = Membership.MemberTypes.MEMBER
        self.assertFalse(self.membership1.is_owner())

    def _assert_membership_is_valid(self, membership):
        try:
            membership.full_clean()
        except (ValidationError, ObjectDoesNotExist):
            self.fail('Test membership should be valid.')

    def _assert_membership_is_invalid(self, membership):
        try:
            membership.full_clean()
        except (ValidationError, ObjectDoesNotExist):
            pass
