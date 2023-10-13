from django.test import TestCase
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from book_clubs.models import User, Club, Membership, Application

class ApplicationModelTestCase(TestCase):

    fixtures = ['book_clubs/tests/fixtures/multiple_applications.json']

    def setUp(self):
        self.user1 = User.objects.get(id = 1)
        self.club1 = Club.objects.get(id = 1)
        self.application1 = Application.objects.get(id = 1)

        self.user2 = User.objects.get(id = 2)
        self.club2 = Club.objects.get(id = 2)
        self.application2 = Application.objects.get(id = 2)

    def test_valid_application(self):
        self._assert_application_is_valid(self.application1)

    def test_club_must_not_be_empty(self):
        self.application1.club = None
        self._assert_application_is_invalid(self.application1)

    def test_club_may_not_be_unique(self):
        self.application1.club = self.application2.club
        self._assert_application_is_valid(self.application1)

    def test_applicant_must_not_be_empty(self):
        self.application1.applicant = None
        self._assert_application_is_invalid(self.application1)

    def test_applicant_may_not_be_unique(self):
        self.application1.applicant = self.application2.applicant
        self._assert_application_is_valid(self.application1)

    def test_club_and_applicant_together_must_be_unique(self):
        self.application1.club = self.application2.club
        self.application1.applicant = self.application2.applicant
        self._assert_application_is_invalid(self.application1)

    def test_must_not_create_application_with_same_club_and_user_as_existing_membership(self):
        self.application1.delete()
        Membership.objects.create(club = self.club1, member = self.user1, member_type = 1)
        self.application1 = Application(club = self.club1, applicant = self.user1)
        self._assert_application_is_invalid(self.application1)

    def _assert_application_is_valid(self, application):
        try:
            application.full_clean()
        except (ValidationError, ObjectDoesNotExist):
            self.fail('Test application should be valid.')

    def _assert_application_is_invalid(self, application):
        try:
            application.full_clean()
        except (ValidationError, ObjectDoesNotExist):
            pass
