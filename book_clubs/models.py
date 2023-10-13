from libgravatar import Gravatar
from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator, MinLengthValidator
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):

    """
        The model for authenticating, and creating a user.
    """

    id = models.AutoField(primary_key = True)
    username = models.CharField(
        max_length = 30,
        unique = True,
        blank = False,
        validators = [
            RegexValidator(
                regex = r'^\w{3,}$',
                message = 'Username must consist of atleast three alphanumeric characters.'
            )
        ]
    )

    email = models.EmailField(
        max_length = 255,
        unique = True,
        blank = False
    )

    first_name = models.CharField(max_length = 50, blank = False)
    last_name = models.CharField(max_length = 50, blank = False)
    location = models.CharField(max_length = 200, null = True, blank = True)

    age = models.IntegerField(
        null = True,
        blank = True,
        validators = [
            MinValueValidator(
                limit_value = 0,
                message = 'Age must not be lower than 0.'
            )
        ]
    )

    # The clubs that a user has memberships to.
    memberships = models.ManyToManyField('Club', through = 'Membership', related_name = 'members')

    # The clubs that a user has applied to.
    applications = models.ManyToManyField('Club', through = 'Application', related_name = 'applicants')

    # The books that a user has ratings for.
    rated = models.ManyToManyField('Book', through = 'Rating', related_name = 'users')

    def gravatar(self, size=120):
       """Return a URL to the user's gravatar."""
       gravatar_object = Gravatar(self.email)
       gravatar_url = gravatar_object.get_image(size=size, default='mp')
       return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=60)

    def __str__(self):
        """String representation of model."""
        return self.username

class Club(models.Model):

    """
        The model for creating a club.
        Note: Unique representation of this model is its id field,
        which is automatically created for every model
        that inherits from models.Model.
    """

    # This is for consistency so that if meeting_cycle is used as something else,
    # for example no longer used as an index and starts from 1 instead.
    MEETING_CYCLE_DEFAULT = 0

    id = models.AutoField(primary_key = True)
    name = models.CharField(max_length = 50, blank = False)
    description = models.CharField(max_length = 1000, blank = True)

    meeting_cycle = models.IntegerField(
        null = False,
        blank = True,
        default = MEETING_CYCLE_DEFAULT,
        validators = [
            MinValueValidator(
                limit_value = MEETING_CYCLE_DEFAULT,
                message = 'Meeting cycle must not be lower than default.'
            )
        ]
    )

    def meeting_cycle_limit_passed(self):
        """Checks whether meeting cycle is greater than or equal to total members + MEETING_CYCLE_DEFAULT."""
        return self.meeting_cycle >= self.members.count() + Club.MEETING_CYCLE_DEFAULT

    def __str__(self):
        """String representation of model."""
        return self.name

    def clean(self):
        """Validation for model."""
        super().clean()

        if ((self.id) and self.meeting_cycle_limit_passed() and (self.meeting_cycle != Club.MEETING_CYCLE_DEFAULT)):
            raise ValidationError("Meeting cycle must not be greater than or equal number of members + the default, while greater than default.")

        if ((not self.id) and (self.meeting_cycle > Club.MEETING_CYCLE_DEFAULT)):
            raise ValidationError("Meeting cycle must not be assigned anything else other than its default upon creation of club.")

    def save(self, *args, **kwargs):
        """Save object."""
        self.full_clean()
        super().save(*args, **kwargs)

class Membership(models.Model):

    """
        The model for creating a unique many-to-many
        relationship between User and Club models.
        User is known as member in this model, and club is club.
        Note: There can be multiple club owners for a single club.
    """

    # Used to set or check the type of member in a membership.
    class MemberTypes(models.IntegerChoices):

        MEMBER = 0, 'Member'
        OWNER = 1, 'Owner'

    id = models.AutoField(primary_key = True)
    club = models.ForeignKey('Club', on_delete = models.CASCADE, blank = False)
    member = models.ForeignKey('User', on_delete = models.CASCADE, blank = False)

    # The type of member in a membership according to MemberTypes.
    member_type = models.IntegerField(
        blank = False,
        choices = MemberTypes.choices
    )

    class Meta:

        """Model options."""

        unique_together = [['club', 'member']]

    def member_type_label(self):
        """Return member_type as label."""
        for member_type_tuple in Membership.MemberTypes.choices:
            if (self.member_type in member_type_tuple):
                return member_type_tuple[1]

    def is_member(self):
        """Checks if member type is member."""
        return (self.member_type == Membership.MemberTypes.MEMBER)

    def is_owner(self):
        """Checks if member type is club owner."""
        return (self.member_type == Membership.MemberTypes.OWNER)

    def clean(self):
        """Validation for model."""
        super().clean()

        if Application.objects.filter(club = self.club, applicant = self.member):
            raise ValidationError('User can not become a member of a club when they have an open application.')

    def save(self, *args, **kwargs):
        """Save object."""
        self.full_clean()
        super().save(*args, **kwargs)

class Application(models.Model):

    """
        The model for creating a unique many-to-many
        relationship between User and Club models.
        User is known as applicant in this model, and club is club.
    """

    id = models.AutoField(primary_key = True)
    club = models.ForeignKey('Club', on_delete = models.CASCADE, blank = False)
    applicant = models.ForeignKey('User', on_delete = models.CASCADE, blank = False)

    class Meta:

        """Model options."""

        unique_together = [['club', 'applicant']]

    def clean(self):
        """Validation for model."""
        super().clean()
        if Membership.objects.filter(club = self.club, member = self.applicant):
            raise ValidationError('User can not apply to a club that they are a member of.')

    def save(self, *args, **kwargs):
        """Save object."""
        self.full_clean()
        super().save(*args, **kwargs)

class Book(models.Model):

    """
        The model for creating a book.
    """

    isbn = models.CharField(
        primary_key = True,
        unique = True,
        blank = False,
        max_length = 10,
        validators = [
            MinLengthValidator(
                10,
                message = 'ISBN must have atleast 10 characters.'
            )
        ]
    )

    name = models.CharField(max_length = 1000, blank = False)
    author = models.CharField(max_length = 1000, blank = False)

    # Year of publication is to be used in terms of UTC + 0 time.
    year_of_publication = models.IntegerField(blank = False)
    publisher = models.CharField(max_length = 1000, blank = False)
    image_url_s = models.URLField(null = True, blank = True)
    image_url_m = models.URLField(null = True, blank = True)
    image_url_l = models.URLField(null = True, blank = True)

    class Meta:

        """Model options."""

        ordering = ['isbn']

    def __str__(self):
        """String representation of model."""
        return self.name

    def clean(self):
        """Validation for model."""
        super().clean()
        if (self.year_of_publication > timezone.now().year):
            raise ValidationError('Year of publication must not be greater than current year.')

    def save(self, *args, **kwargs):
        """Save object."""
        self.full_clean()
        super().save(*args, **kwargs)

class Rating(models.Model):

    """
        The model for creating a unique many-to-many
        relationship between User and Book models.
    """

    id = models.AutoField(primary_key = True)
    user = models.ForeignKey('User', on_delete = models.CASCADE, blank = False)
    book = models.ForeignKey('Book', on_delete = models.CASCADE, blank = False)

    rating = models.IntegerField(blank = False,
        validators = [
            MinValueValidator(
                limit_value = 0,
                message = 'Rating must not be lower than 0.'
            ),
            MaxValueValidator(
                limit_value = 10,
                message = 'Rating must not be greater than 10.'
            )
        ]
    )

    class Meta:

        """Model options."""

        unique_together = [['user', 'book']]

class Meeting(models.Model):

    """
        The model for creating a meeting.
    """

    id = models.AutoField(primary_key = True)
    club = models.ForeignKey('Club', on_delete = models.CASCADE, blank = False)
    book_chooser = models.ForeignKey('User', on_delete = models.SET_NULL, null = True, blank = True)
    chosen_book = models.ForeignKey('Book', on_delete = models.SET_NULL, null = True, blank = True)
    active = models.BooleanField(default = True, blank = False)
    deadline = models.DateTimeField(blank = False)

    # The books that a meeting is recommended to.
    recommendations = models.ManyToManyField('Book', through = 'MeetingRecommendation', related_name = 'recommended_in')

    def passed_deadline(self):
        """Checks if deadline is passed."""
        return self.deadline <= timezone.now()

    class Meta:

        """Model options."""

        ordering = ['deadline']

    def clean(self):
        """Validation for model."""
        super().clean()

        if ((self.book_chooser) and (self.book_chooser not in self.club.members.all())):
            raise ValidationError('Book chooser must be a member of club.')

        if ((self.deadline < timezone.now())):
            if (not self.id):
                raise ValidationError('Must not set deadline to be before now on meeting creation.')

            if ((self.id) and (Meeting.objects.get(id = self.id).deadline != self.deadline)):
                raise ValidationError('Must not change deadline to be before now.')

    def save(self, *args, **kwargs):
        """Save object."""
        self.full_clean()
        super().save(*args, **kwargs)

class MeetingRecommendation(models.Model):

    """
        The model for creating a unique many-to-many
        relationship between Meeting and Book models.
    """

    id = models.AutoField(primary_key = True)
    meeting = models.ForeignKey('Meeting', on_delete = models.CASCADE, blank = False)
    book = models.ForeignKey('Book', on_delete = models.CASCADE, blank = False)

    class Meta:

        """Model options."""

        unique_together = [['meeting', 'book']]

class Message(models.Model):
    """The data model for sending messages in the meeting chat."""

    id = models.AutoField(primary_key = True)
    meeting = models.ForeignKey('Meeting', on_delete = models.CASCADE, blank = False)
    name_of_user = models.CharField(max_length = 30, blank = False)
    value = models.CharField(max_length = 1000000, blank = False)
    post_time = models.DateTimeField(default = timezone.now, blank = False)

    def post_time_visual_output(self):
        """Outputs the post time as more appealing."""
        return f'{self.post_time.hour} : {self.post_time.minute}'
