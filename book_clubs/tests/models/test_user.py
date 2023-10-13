from django.test import TestCase
from django.core.exceptions import ValidationError
from book_clubs.models import User

class UserModelTestCase(TestCase):

    fixtures = ['book_clubs/tests/fixtures/multiple_users.json']

    def setUp(self):
        self.user1 = User.objects.get(id = 1)
        self.user2 = User.objects.get(id = 2)

    def test_valid_user(self):
        self._assert_user_is_valid(self.user1)

    def test_username_must_not_be_blank(self):
        self.user1.username = ''
        self._assert_user_is_invalid(self.user1)

    def test_username_must_be_unique(self):
        self.user1.username = self.user2.username
        self._assert_user_is_invalid(self.user1)

    def test_username_must_have_3_characters(self):
        self.user1.username = 't1'
        self._assert_user_is_invalid(self.user1)

    def test_username_must_be_not_be_greater_than_30_characters(self):
        self.user1.username = ('a' * 30) + '1'
        self._assert_user_is_invalid(self.user1)

    def test_username_may_be_only_alphabetical(self):
        self.user1.username = 'test'
        self._assert_user_is_valid(self.user1)

    def test_username_may_be_only_numerical(self):
        self.user1.username = '123'
        self._assert_user_is_valid(self.user1)

    def test_email_must_not_be_blank(self):
        self.user1.email = ''
        self._assert_user_is_invalid(self.user1)

    def test_email_must_be_unique(self):
        self.user1.email = self.user2.email
        self._assert_user_is_invalid(self.user1)

    def test_email_must_contain_username(self):
        self.user1.email = '@example.org'
        self._assert_user_is_invalid(self.user1)

    def test_email_must_contain_at_symbol(self):
        self.user1.email = 'test1example.org'
        self._assert_user_is_invalid(self.user1)

    def test_email_must_contain_domain_name(self):
        self.user1.email = 'test1@.org'
        self._assert_user_is_invalid(self.user1)

    def test_email_must_contain_domain(self):
        self.user1.email = 'test1@example'
        self._assert_user_is_invalid(self.user1)

    def test_email_must_contain_only_one_at_symbol(self):
        self.user1.email = 'test1@@example.org'
        self._assert_user_is_invalid(self.user1)

    def test_email_must_not_be_greater_than_255_characters(self):
        self.user1.email = ('a' * 255) + '@example.org'
        self._assert_user_is_invalid(self.user1)

    def test_first_name_must_not_be_blank(self):
        self.user1.first_name = ''
        self._assert_user_is_invalid(self.user1)

    def test_first_name_may_be_not_unique(self):
        self.user1.first_name = self.user2.first_name
        self._assert_user_is_valid(self.user1)

    def test_first_name_must_not_be_greater_than_50_characters(self):
        self.user1.first_name = 'a' * 51
        self._assert_user_is_invalid(self.user1)

    def test_last_name_must_not_be_blank(self):
        self.user1.last_name = ''
        self._assert_user_is_invalid(self.user1)

    def test_last_name_may_be_not_unique(self):
        self.user1.last_name = self.user2.last_name
        self._assert_user_is_valid(self.user1)

    def test_last_name_must_not_be_greater_than_50_characters(self):
        self.user1.last_name = 'a' * 51
        self._assert_user_is_invalid(self.user1)

    def test_location_may_be_blank(self):
        self.user1.location = ''
        self._assert_user_is_valid(self.user1)

    def test_location_may_be_not_unique(self):
        self.user1.location = self.user2.location
        self._assert_user_is_valid(self.user1)

    def test_location_must_not_be_greater_than_200_characters(self):
        self.user1.last_name = 'a' * 201
        self._assert_user_is_invalid(self.user1)

    def test_age_may_be_empty(self):
        self.user1.age = None
        self._assert_user_is_valid(self.user1)

    def test_age_must_not_be_lesser_than_0(self):
        self.user1.age = -1
        self._assert_user_is_invalid(self.user1)

    def test_str_returns_username(self):
        self.assertTrue(self.user1.__str__() == self.user1.username)

    def _assert_user_is_valid(self, user):
        try:
            user.full_clean()
        except (ValidationError):
            self.fail('Test user should be valid.')

    def _assert_user_is_invalid(self, user):
        with self.assertRaises(ValidationError):
            user.full_clean()
