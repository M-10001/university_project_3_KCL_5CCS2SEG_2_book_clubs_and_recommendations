from book_clubs.models import User, Club, Membership
from django.test import TestCase
from django.urls import reverse
from book_clubs.tests.helpers import LogInTester,reverse_with_next

class DisbandClubTestCase(TestCase, LogInTester):
    """Tests of the disband club view."""

    fixtures = ['book_clubs/tests/fixtures/multiple_memberships.json']

    def setUp(self):
        self.user1 = User.objects.get(id = 1)
        self.club1 = Club.objects.get(id = 1)
        self.club2 = Club.objects.get(id = 2)
        self.membership1 = Membership.objects.get(id = 1)
        self.url = reverse('disband_club', kwargs={'club_id' : self.club1.id})

    def test_disband_club(self):
        self.assertEqual(self.url, f'/disband_club/1/')

    def test_get_disband_club(self):
        self.client.login(username = self.user1.username, password = 'Password123')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'disband_club.html')
        form = response.context['confirmation_form']
        self.assertFalse(form.is_bound)

    def test_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code = 302, target_status_code = 200)

    def test_invalid_club_id(self):
        self.client.login(username = self.user1.username, password = 'Password123')
        self.url = reverse('disband_club', kwargs = {'club_id' : 0})
        redirect_url = reverse('user_club_list')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code = 302, target_status_code = 200)

    def test_when_not_member_of_club(self):
        self.client.login(username = self.user1.username, password = 'Password123')
        redirect_url = reverse('user_club_list')
        self.url = reverse('disband_club', kwargs = {'club_id' : self.club2.id})
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code = 302, target_status_code = 200)

    def test_not_owner_of_club(self):
        self.client.login(username = self.user1.username, password = 'Password123')
        self.membership1.member_type = Membership.MemberTypes.MEMBER
        self.membership1.save()
        redirect_url = reverse('club_page', kwargs = {'club_id' : self.club1.id})
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code = 302, target_status_code = 200)

    def test_post_with_true_form_input(self):
        self.client.login(username = self.user1.username, password = 'Password123')
        redirect_url = reverse('user_club_list')
        club_before_count = len(Club.objects.all())
        response = self.client.post(self.url, {'confirmation' : True})
        club_after_count = len(Club.objects.all())
        self.assertRedirects(response, redirect_url, status_code = 302, target_status_code = 200)
        self.assertEqual(club_after_count, club_before_count - 1)

    def test_post_with_false_form_input(self):
        self.client.login(username = self.user1.username, password = 'Password123')
        redirect_url = reverse('club_page', kwargs = {'club_id' : self.club1.id})
        club_before_count = len(Club.objects.all())
        response = self.client.post(self.url, {'confirmation' : 'False'})
        club_after_count = len(Club.objects.all())
        self.assertRedirects(response, redirect_url, status_code = 302, target_status_code = 200)
        self.assertEqual(club_after_count, club_before_count)
