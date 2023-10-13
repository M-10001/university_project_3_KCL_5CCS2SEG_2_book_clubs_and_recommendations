from django.test import TestCase
from django.urls import reverse
from book_clubs.models import User, Club, Membership, Application
from book_clubs.tests.helpers import LogInTester, reverse_with_next

class ClubApplicationListTestCase(TestCase, LogInTester):
    """User club application list tests."""

    fixtures = ['book_clubs/tests/fixtures/single_application_and_membership.json']

    def setUp(self):
        self.user = User.objects.get(id = 1)
        self.club = Club.objects.get(id = 1)
        self.url = reverse('club_application_list', kwargs = {'club_id' : self.club.id})

    def test_url(self):
        self.assertEqual(self.url,'/club_application_list/1/')

    def test_get_club_application_list(self):
        self.client.login(username = 'test1', password = 'Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_application_list.html')
        applications = response.context['applications']
        self.assertEqual(len(applications), len(Application.objects.filter(club=self.club)))

    def test_get_club_application_list_when_not_owner(self):
        membership = Membership.objects.get(id = 1)
        membership.member_type = Membership.MemberTypes.MEMBER
        membership.save()
        self.client.login(username = 'test1', password = 'Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow = True)
        response_url = reverse('club_page', kwargs = {'club_id' : self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_get_club_application_list_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        response = self.client.get(self.url)
        response_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
