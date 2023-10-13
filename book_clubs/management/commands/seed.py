from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
import csv, random
from book_clubs.models import User, Club, Membership, Application, Book

class Command(BaseCommand):
    """The database seeder."""

    PASSWORD = "Password123"
    TOTAL_USERS = 200
    OWNER_COUNT_PER_CLUB = 1
    MEMBER_COUNT_PER_CLUB = 20
    APPLICANT_COUNT_PER_CLUB = 5

    def __init__(self):
        super().__init__()

    def handle(self, *args, **options):
        book_models = []

        with open('book_clubs/management/BX_Books.csv', newline = '', encoding = 'Windows-1252') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter = ';', quoting = csv.QUOTE_ALL)
            next(csv_reader)

            for row in csv_reader:
                book = Book(
                    isbn = row[0],
                    name = row[1],
                    author = row[2],
                    year_of_publication = row[3],
                    publisher = row[4],
                    image_url_s = row[5],
                    image_url_m = row[6],
                    image_url_l = row[7]
                )
                
                try:
                    book.full_clean()
                except ValidationError:
                    pass
                else:
                    book_models.append(book)

        Book.objects.bulk_create(book_models)
        print('Total books seeded: '+ str(Book.objects.count()))
        print()

        clubs = []
        club = None
        owner_count = 0
        member_count = 0
        application_count = 0

        if clubs:
            club = clubs.pop(0)
            owner_count = Membership.objects.filter(club = club, member_type = Memberhip.MemberTypes.OWNER).count()
            member_count = Membership.objects.filter(club = club, member_type = Memberhip.MemberTypes.MEMBER).count()
            application_count = club.applicants.count()
        else:
            club = self._seed_club(1)

        print(f'Clubs seeded: {Club.objects.count()}',  end='\r')
        print()
        print(f'Seeding users for club with ID: {club.id}',  end='\r')
        print()
        print()

        id = 1
        users_seeded = User.objects.count()

        while (users_seeded <= Command.TOTAL_USERS):
            user = self._seed_user(id)

            if user:
                if (owner_count < Command.OWNER_COUNT_PER_CLUB):
                    Membership.objects.create(club = club, member = user, member_type = Membership.MemberTypes.OWNER)
                    owner_count = owner_count + 1
                elif (member_count < Command.MEMBER_COUNT_PER_CLUB):
                    Membership.objects.create(club = club, member = user, member_type = Membership.MemberTypes.MEMBER)
                    member_count = member_count + 1
                elif (application_count < Command.APPLICANT_COUNT_PER_CLUB):
                    Application.objects.create(club = club, applicant = user)
                    application_count = application_count + 1
                else:
                    print(f'Total owners seeded: {Membership.objects.filter(member_type = Membership.MemberTypes.OWNER).count()}',  end='\r')
                    print()
                    print(f'Total members seeded: {Membership.objects.filter(member_type = Membership.MemberTypes.MEMBER).count()}',  end='\r')
                    print()
                    print(f'Total applications seeded: {Application.objects.count()}',  end='\r')
                    print()
                    print()
                    print()

                    if clubs:
                        club = clubs.pop(0)
                        owner_count = Membership.objects.filter(club = club, member_type = Memberhip.MemberTypes.OWNER)
                        member_count = Membership.objects.filter(club = club, member_type = Memberhip.MemberTypes.MEMBER)
                        application_count = club.applicants.count()
                    else:
                        club = self._seed_club(Club.objects.count() + 1)
                        owner_count = 0
                        member_count = 0
                        application_count = 0
                        print(f'Clubs seeded: {Club.objects.count()}',  end='\r')
                        print()

                    print(f'Seeding users for club with ID: {club.id}',  end='\r')
                    print()
                    print()

                users_seeded = users_seeded + 1

            id = id + 1

        print(f'Total owners seeded: {Membership.objects.filter(member_type = Membership.MemberTypes.OWNER).count()}',  end='\r')
        print()
        print(f'Total members seeded: {Membership.objects.filter(member_type = Membership.MemberTypes.MEMBER).count()}',  end='\r')
        print()
        print(f'Total applications seeded: {Application.objects.count()}',  end='\r')

    def _seed_user(self, id):

        user = None

        if (id < 10):
            username = str(id) + 'aa'
        elif (id < 100):
            username = str(id) + 'a'
        else:
            username = str(id)

        try:
            user = User.objects.create_user(
                id = id,
                username = username,
                email = f'test{id}@example.org',
                first_name = f'test{id}_f',
                last_name = f'test{id}_l',
                password = Command.PASSWORD
            )
        except:
            pass

        return user

    def _seed_club(self, id):
        seeded = False
        club = None

        club = Club.objects.create(
            id = id,
            name = 'temp',
            description = self._create_club_description()
        )

        return club

    def _create_club_description(self):
        random_number = random.randint(0, 1000)
        return 'x' * random_number
