from django.test import TestCase
from django.urls import reverse
from book_clubs.forms import ClubCreationForm
from book_clubs.models import User, Club, Membership
from book_clubs.tests.helpers import LogInTester, reverse_with_next

class CreateClubViewTestCase(TestCase, LogInTester):
    """Tests of the create club view."""

    fixtures = [
        'book_clubs/tests/fixtures/multiple_users.json',
        'book_clubs/tests/fixtures/multiple_clubs.json'
        ]

    def setUp(self):
        self.url = reverse('create_club')
        self.user = User.objects.get(email='test1@example.org')
        self.user2 = User.objects.get(email='test2@example.org')
        self.form_input = {
            'name': 'Test Book Club',
            'description': 'This is a book club.'
            }

    def test_create_club_url(self):
        self.assertEqual(self.url,'/create_club/')

    def test_get_create_club_when_logged_in(self):
        self.client.login(username=self.user.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_club.html')
        club_form = response.context['club_form']
        self.assertTrue(isinstance(club_form, ClubCreationForm))
        self.assertFalse(club_form.is_bound)

    def test_get_create_club_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        response = self.client.get(self.url)
        response_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_successful_create_club_and_ownership(self):
       self.client.login(username=self.user.username, password="Password123")
       self.assertTrue(self._is_logged_in())
       club_before_count = Club.objects.count()
       membership_before_count = Membership.objects.count()
       response = self.client.post(self.url, self.form_input, follow=True)
       club_after_count = Club.objects.count()
       membership_after_count = Membership.objects.count()
       self.assertEqual(club_after_count, club_before_count+1)
       self.assertEqual(membership_after_count, membership_before_count+1)
       club = Club.objects.get(name = 'Test Book Club')
       self.assertEqual(club.name, "Test Book Club")
       self.assertEqual(club.description, "This is a book club.")
       membership = Membership.objects.get(club=club, member=self.user)
       response_url = reverse('club_page', kwargs = {'club_id' : club.id})
       self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
       self.assertTemplateUsed(response, 'club_page.html')

    def test_unsuccessful_create_club_and_ownership(self):
        self.client.login(username=self.user.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        self.form_input['name'] = ""
        club_before_count = Club.objects.count()
        membership_before_count = Membership.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        club_after_count = Club.objects.count()
        membership_after_count = Membership.objects.count()
        self.assertEqual(club_after_count, club_before_count)
        self.assertEqual(membership_after_count, membership_before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_club.html')
        club_form = response.context['club_form']
        self.assertTrue(isinstance(club_form, ClubCreationForm))
        self.assertTrue(club_form.is_bound)
