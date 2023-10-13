from django.utils import timezone
from django.test import TestCase
from django.core.exceptions import ValidationError
from book_clubs.models import Book

class BookModelTestCase(TestCase):

    fixtures = ['book_clubs/tests/fixtures/multiple_books.json']

    def setUp(self):
        self.book1 = Book.objects.get(isbn = '0000000001')
        self.book2 = Book.objects.get(isbn = '0000000002')

    def test_valid_book(self):
        self._assert_book_is_valid(self.book1)

    def test_isbn_must_not_have_lesser_than_10_characters(self):
        self.book1.delete()
        self.book1.isbn = '00000000A'
        self._assert_book_is_invalid(self.book1)

    def test_isbn_must_not_have_more_than_10_characters(self):
        self.book1.delete()
        self.book1.isbn = '0000000000A'
        self._assert_book_is_invalid(self.book1)

    def test_name_must_not_be_blank(self):
        self.book1.name = ''
        self._assert_book_is_invalid(self.book1)

    def test_name_may_be_not_unique(self):
        self.book1.name = self.book2.name
        self._assert_book_is_valid(self.book1)

    def test_name_must_not_be_greater_than_1000_characters(self):
        self.book1.name = 'a' * 1001
        self._assert_book_is_invalid(self.book1)

    def test_author_must_not_be_blank(self):
        self.book1.author = ''
        self._assert_book_is_invalid(self.book1)

    def test_author_may_be_not_unique(self):
        self.book1.author = self.book2.author
        self._assert_book_is_valid(self.book1)

    def test_author_must_not_be_greater_than_1000_characters(self):
        self.book1.author = 'a' * 1001
        self._assert_book_is_invalid(self.book1)

    def test_year_of_publication_may_be_not_unique(self):
        self.book1.year_of_publication = self.book2.year_of_publication
        self._assert_book_is_valid(self.book1)

    def test_year_of_publication_must_not_be_greater_than_current_year(self):
        self.book1.year_of_publication = timezone.now().year + 1
        self._assert_book_is_invalid(self.book1)

    def test_publisher_must_not_be_blank(self):
        self.book1.publisher = ''
        self._assert_book_is_invalid(self.book1)

    def test_publisher_may_be_not_unique(self):
        self.book1.publisher = self.book2.publisher
        self._assert_book_is_valid(self.book1)

    def test_publisher_must_not_be_greater_than_1000_characters(self):
        self.book1.publisher = 'a' * 1001
        self._assert_book_is_invalid(self.book1)

    def _assert_book_is_valid(self, book):
        try:
            book.full_clean()
        except (ValidationError):
            self.fail('Test book should be valid.')

    def _assert_book_is_invalid(self, book):
        with self.assertRaises(ValidationError):
            book.full_clean()
