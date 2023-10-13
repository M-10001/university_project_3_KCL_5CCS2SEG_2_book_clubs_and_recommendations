from django.test import TestCase
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from book_clubs.models import Book, Meeting, MeetingRecommendation

class ApplicationModelTestCase(TestCase):

    fixtures = ['book_clubs/tests/fixtures/multiple_meeting_recommendations.json']

    def setUp(self):
        self.meeting_recommendation1 = MeetingRecommendation.objects.get(id = 1)
        self.meeting_recommendation2 = MeetingRecommendation.objects.get(id = 2)

    def test_valid_meeting_recommendation(self):
        self._assert_meeting_recommendation_is_valid(self.meeting_recommendation1)

    def test_meeting_must_not_be_empty(self):
        self.meeting_recommendation1.meeting = None
        self._assert_meeting_recommendation_is_invalid(self.meeting_recommendation1)

    def test_meeting_may_not_be_unique(self):
        self.meeting_recommendation1.meeting = self.meeting_recommendation2.meeting
        self._assert_meeting_recommendation_is_valid(self.meeting_recommendation1)

    def test_book_must_not_be_empty(self):
        self.meeting_recommendation1.book = None
        self._assert_meeting_recommendation_is_invalid(self.meeting_recommendation1)

    def test_book_may_not_be_unique(self):
        self.meeting_recommendation1.book = self.meeting_recommendation2.book
        self._assert_meeting_recommendation_is_valid(self.meeting_recommendation1)

    def test_meeting_and_book_together_must_be_unique(self):
        self.meeting_recommendation1.meeting = self.meeting_recommendation2.meeting
        self.meeting_recommendation1.book = self.meeting_recommendation2.book
        self._assert_meeting_recommendation_is_invalid(self.meeting_recommendation1)

    def _assert_meeting_recommendation_is_valid(self, meeting_recommendation):
        try:
            meeting_recommendation.full_clean()
        except (ValidationError, ObjectDoesNotExist):
            self.fail('Test meeting recommendation should be valid.')

    def _assert_meeting_recommendation_is_invalid(self, meeting_recommendation):
        try:
            meeting_recommendation.full_clean()
        except (ValidationError, ObjectDoesNotExist):
            pass
