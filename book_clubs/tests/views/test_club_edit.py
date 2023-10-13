from book_clubs.models import User, Club, Membership
from django.test import TestCase
from django.urls import reverse
from book_clubs.tests.helpers import LogInTester,reverse_with_next

class ClubEditTestCase(TestCase, LogInTester):
    """Tests of the club edit view."""

    fixtures = ['book_clubs/tests/fixtures/multiple_memberships.json']

    def setUp(self):
        self.user1 = User.objects.get(id = 1)
        self.user2 = User.objects.get(id = 2)
        self.club1 = Club.objects.get(id = 1)
        self.membership1 = Membership.objects.get(id = 1)
        self.url = reverse('club_edit', kwargs = {'club_id' : self.club1.id})
        self.form_input = {'name' : 'test1_c', 'description' : 'Random text 123 c'}

    def test_url(self):
        self.assertEqual(self.url, '/club_edit/1/')

    def test_get(self):
        self.client.login(username = self.user1.username, password = 'Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_edit.html')
        self.assertFalse(response.context['club_form'].is_bound)

    def test_logged_out(self):
        self.assertFalse(self._is_logged_in())
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code = 302, target_status_code = 200)

    def test_invalid_club_id(self):
        self.client.login(username = self.user1.username, password = 'Password123')
        self.assertTrue(self._is_logged_in())
        self.url = reverse('club_edit', kwargs = {'club_id' : 0})
        redirect_url = reverse('user_club_list')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code = 302, target_status_code = 200)

    def test_user_not_member_of_club(self):
        self.client.login(username = self.user2.username, password = 'Password123')
        self.assertTrue(self._is_logged_in())
        redirect_url = reverse('user_club_list')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code = 302, target_status_code = 200)

    def test_user_not_owner_of_club(self):
        self.client.login(username = self.user1.username, password = 'Password123')
        self.assertTrue(self._is_logged_in())
        self.membership1.member_type = Membership.MemberTypes.MEMBER
        self.membership1.save()
        redirect_url = reverse('club_page', kwargs = {'club_id' : self.club1.id})
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code = 302, target_status_code = 200)

    def test_invalid_form(self):
        self.client.login(username = self.user1.username, password = 'Password123')
        self.assertTrue(self._is_logged_in())
        self.form_input['name'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['club_form'].is_bound)

    def test_valid_form(self):
        self.client.login(username = self.user1.username, password = 'Password123')
        self.assertTrue(self._is_logged_in())
        redirect_url = reverse('club_page', kwargs = {'club_id' : self.club1.id})
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response, redirect_url, status_code = 302, target_status_code = 200)
