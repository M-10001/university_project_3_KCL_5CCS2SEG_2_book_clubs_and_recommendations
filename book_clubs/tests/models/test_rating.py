from django.test import TestCase
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from book_clubs.models import User, Book, Rating

class RatingModelTestCase(TestCase):

    fixtures = ['book_clubs/tests/fixtures/multiple_ratings.json']

    def setUp(self):
        self.rating1 = Rating.objects.get(id = 1)
        self.rating2 = Rating.objects.get(id = 2)

    def test_valid_rating(self):
        self._assert_rating_is_valid(self.rating1)

    def test_user_must_not_be_empty(self):
        self.rating1.user = None
        self._assert_rating_is_invalid(self.rating1)

    def test_book_must_not_be_empty(self):
        self.rating1.book = None
        self._assert_rating_is_invalid(self.rating1)

    def test_user_and_book_together_must_be_unique(self):
        self.rating1.user = self.rating2.user
        self.rating1.book = self.rating2.book
        self._assert_rating_is_invalid(self.rating1)

    def test_rating_must_be_between_and_including_0_and_10(self):
        self.rating1.rating = -1
        self._assert_rating_is_invalid(self.rating1)
        self.rating1.rating = 11
        self._assert_rating_is_invalid(self.rating1)

    def _assert_rating_is_valid(self, rating):
        try:
            rating.full_clean()
        except (ValidationError, ObjectDoesNotExist):
            self.fail('Test rating should be valid.')

    def _assert_rating_is_invalid(self, rating):
        try:
            rating.full_clean()
        except (ValidationError, ObjectDoesNotExist):
            pass
