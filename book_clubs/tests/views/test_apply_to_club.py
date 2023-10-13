from django.test import TestCase
from django.urls import reverse
from book_clubs.models import User, Club, Application, Membership
from book_clubs.tests.helpers import LogInTester, reverse_with_next

class ApplyToClubViewTestCase(TestCase, LogInTester):

    fixtures = ['book_clubs/tests/fixtures/single_application_and_membership_and_user.json',]

    def setUp(self):
        self.url = reverse('apply_to_club', kwargs = {'club_id' : 1})
        self.user1 = User.objects.get(id = 1)
        self.user2 = User.objects.get(id = 2)
        self.user3 = User.objects.get(id = 3)
        self.application = Application.objects.get(id = 1)
        self.membership = Membership.objects.get(id = 1)
        self.club = Club.objects.get(id = 1)

    def test_apply_to_club_url(self):
        self.assertEqual(self.url, '/apply_to_club/1/')

    def test_apply_to_club_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        response = self.client.get(self.url)
        response_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, response_url, status_code = 302, target_status_code = 200)

    def test_successful_apply_to_club(self):
            self.client.login(username = self.user3.username, password='Password123')
            self.assertTrue(self._is_logged_in())
            initial_application_count = Application.objects.filter(club=self.club).count()
            response = self.client.get(self.url, follow=True)
            response_url = reverse('applicable_clubs')
            self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
            after_application_count = Application.objects.filter(club=self.club).count()
            self.assertEqual(after_application_count, initial_application_count+1)

    def test_unsuccessful_apply_to_club_already_applicant(self):
            self.client.login(username = self.user2.username, password='Password123')
            self.assertTrue(self._is_logged_in())
            initial_application_count = Application.objects.filter(club=self.club).count()
            response = self.client.get(self.url, follow=True)
            response_url = reverse('applicable_clubs')
            self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
            after_application_count = Application.objects.filter(club=self.club).count()
            self.assertEqual(after_application_count, initial_application_count)

    def test_unsuccessful_apply_to_club_already_member(self):
            self.client.login(username = self.user1.username, password='Password123')
            self.assertTrue(self._is_logged_in())
            initial_application_count = Application.objects.filter(club=self.club).count()
            response = self.client.get(self.url, follow=True)
            response_url = reverse('applicable_clubs')
            self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
            after_application_count = Application.objects.filter(club=self.club).count()
            self.assertEqual(after_application_count, initial_application_count)
