from django.core.management.base import BaseCommand, CommandError
from book_clubs.models import User, Club, Book

class Command(BaseCommand):
    """The database unseeder."""

    def handle(self, *args, **options):
        User.objects.all().filter(is_staff = False).delete()
        Club.objects.all().delete()
        Book.objects.all().delete()
