from django.test import TestCase
from django.urls import reverse
from book_clubs.models import User, Club, Application, Membership
from book_clubs.tests.helpers import LogInTester, reverse_with_next

class CreateAcceptApplicationTestCase(TestCase, LogInTester):
    """Tests of the accept application view."""

    fixtures = [
        'book_clubs/tests/fixtures/single_application_and_membership.json'
        ]

    def setUp(self):
        self.user1 = User.objects.get(id = 1)
        self.user2 = User.objects.get(id = 2)
        self.application = Application.objects.get(id = 1)
        self.club = Club.objects.get(id = 1)
        self.url = reverse('accept_application', kwargs = {'user_id' : 2, 'club_id' : 1})

    def test_get_url(self):
        self.assertEqual(self.url, '/accept_application/2/1/')

    def test_successful_acception_of_application(self):
        self.client.login(username = self.user1.username, password = 'Password123')
        self.assertTrue(self._is_logged_in())
        initial_application_count = Application.objects.filter(club = self.club).count()
        initial_membership_count = Membership.objects.filter(club = self.club).count()
        response = self.client.get(self.url, follow = True)
        response_url = reverse('club_application_list', kwargs = {'club_id' : 1})
        self.assertRedirects(response, response_url, status_code = 302, target_status_code = 200)
        after_application_count = Application.objects.filter(club = self.club).count()
        after_membership_count = Membership.objects.filter(club = self.club).count()
        self.assertEqual(after_application_count, initial_application_count - 1)
        self.assertEqual(after_membership_count, initial_membership_count + 1)

    def test_user_is_not_owner_and_unsuccessful_acception_of_application(self):
        membership = Membership.objects.get(member = self.user1, club = self.club)
        membership.member_type = Membership.MemberTypes.MEMBER
        membership.save()
        self.client.login(username = self.user1.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        initial_application_count = Application.objects.filter(club=self.club).count()
        initial_membership_count = Membership.objects.filter(club=self.club).count()
        response = self.client.get(self.url, follow=True)
        response_url = reverse('club_page', kwargs = {'club_id' : 1})
        self.assertRedirects(response, response_url, status_code = 302, target_status_code=200)
        after_application_count = Application.objects.filter(club = self.club).count()
        after_membership_count = Membership.objects.filter(club = self.club).count()
        self.assertEqual(after_application_count, initial_application_count)
        self.assertEqual(after_membership_count, initial_membership_count)

    def test_get_accept_application_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        response = self.client.get(self.url)
        response_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
