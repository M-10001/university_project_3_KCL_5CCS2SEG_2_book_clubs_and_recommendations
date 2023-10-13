from django.utils import timezone
from django import forms
from .models import User, Club, Membership, Application, Book, Meeting
from django.core.validators import RegexValidator

class ClubCreationForm(forms.ModelForm):
    """Enables creation of clubs."""

    class Meta:
        """Form options"""

        model = Club
        fields = ['name', 'description']
        widgets = {'description' : forms.Textarea()}
        labels = {'name' : 'Name', 'description' : 'Description'}

class LogInForm(forms.Form):
    username = forms.CharField(label = 'Username')
    password = forms.CharField(label = 'Password', widget = forms.PasswordInput())

class SignUpForm(forms.ModelForm):
    """Enables creation of a new user."""
    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'age', 'username', 'email', 'location']
        labels = {'age' : 'Age (optional)', 'location' : 'Location (Optional)'}

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain a lowercase character and a number.'
        )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Form validation."""
        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')


    def save(self):
        """Saves a new user."""
        super().save(commit=False)
        user = User.objects.create_user(
            username = self.cleaned_data.get('username'),
            email = self.cleaned_data.get('email'),
            first_name = self.cleaned_data.get('first_name'),
            last_name = self.cleaned_data.get('last_name'),
            age = self.cleaned_data.get('age'),
            location = self.cleaned_data.get('location'),
            password = self.cleaned_data.get('new_password')
        )
        return user

class ConfirmationForm(forms.Form):
    """Enables input of yes or no answer."""
    confirmation = forms.ChoiceField(label = 'Confirmation', choices= ((False,'No'),(True,'Yes')))

class SearchBooksForm(forms.Form):
    """Enables searching of books."""

    isbn = forms.CharField(label = 'ISBN', required = False)
    name = forms.CharField(label = 'Book name', required = False)
    author = forms.CharField(label = 'Author', required = False)
    year_of_publication = forms.IntegerField(label = 'Year of publication', required = False)
    publisher = forms.CharField(label = 'Publisher', required = False)

class MeetingCreationForm(forms.Form):
    """Enables creation of a meeting."""

    deadline = forms.DateTimeField(label = 'Deadline(UTC+0) Format[YYYY-MM-DD HH:MM(:SS.)]')

    def clean(self):
        """Form validation."""
        super().clean()
        deadline = self.cleaned_data.get('deadline')

        if (deadline <= timezone.now()):
            self.add_error('deadline', 'Must not set deadline to be before now on meeting creation.')
