from book_clubs.models import User, Club, Membership
from django.test import TestCase
from django.urls import reverse
from book_clubs.tests.helpers import LogInTester,reverse_with_next

class KickMemberTestCase(TestCase, LogInTester):
    """Tests of the kick member view."""

    fixtures = ['book_clubs/tests/fixtures/single_club_different_memberships.json']

    def setUp(self):
        self.url = reverse('kick_member', kwargs={'user_id' : 2, 'club_id': 1})
        self.user2 = User.objects.get(id = 2)
        self.user3 = User.objects.get(id = 3)
        self.club1 = Club.objects.get(id = 1)
        self.membership1 = Membership.objects.get(id = 1)
        self.membership2 = Membership.objects.get(id = 2)
        self.membership3 = Membership.objects.get(id = 3)
        self.membership4 = Membership.objects.get(id = 4)

    def test_kick_member_url(self):
        self.assertEqual(self.url, f'/kick_member/2/1/')

    def test_get_kick_member(self):
        self.client.login(username = 'test1', password = 'Password123')
        self.assertTrue(self._is_logged_in())
        memberships_before_count = len(Membership.objects.filter(club = self.club1))
        response = self.client.get(self.url)
        memberships_after_count = len(Membership.objects.filter(club = self.club1))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'kick_member.html')
        self.assertEqual(memberships_after_count, memberships_before_count)

    def test_get_kick_member_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code = 302, target_status_code = 200)

    def test_get_kick_member_when_invalid_user_id(self):
        self.client.login(username = 'test1', password = 'Password123')
        self.assertTrue(self._is_logged_in())
        self.url = reverse('kick_member', kwargs={'user_id' : 0, 'club_id': self.club1.id})
        redirect_url = reverse('member_list', kwargs = {'club_id' : self.club1.id})
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code = 302, target_status_code = 200)

    def test_get_kick_member_when_user_of_user_id_is_not_member(self):
        self.client.login(username = 'test1', password = 'Password123')
        self.assertTrue(self._is_logged_in())
        self.membership2.delete()
        redirect_url = reverse('member_list', kwargs = {'club_id' : self.club1.id})
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code = 302, target_status_code = 200)

    def test_get_kick_member_when_user_of_user_id_is_owner(self):
        self.client.login(username = 'test1', password = 'Password123')
        self.assertTrue(self._is_logged_in())
        self.url = reverse('kick_member', kwargs = {'user_id' : self.user3.id, 'club_id' : self.club1.id})
        redirect_url = reverse('member_list', kwargs = {'club_id' : self.club1.id})
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code = 302, target_status_code = 200)

    def test_get_kick_member_when_invalid_club_id(self):
        self.client.login(username = 'test1', password = 'Password123')
        self.assertTrue(self._is_logged_in())
        self.url = reverse('kick_member', kwargs={'user_id' : self.user2.id, 'club_id': 0})
        redirect_url = reverse('user_club_list')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code = 302, target_status_code = 200)

    def test_get_kick_member_when_user_is_not_member(self):
        self.client.login(username = 'test1', password = 'Password123')
        self.assertTrue(self._is_logged_in())
        self.membership1.delete()
        redirect_url = reverse('user_club_list')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code = 302, target_status_code = 200)

    def test_post_kick_member_with_true_form_input(self):
        self.client.login(username = 'test1', password = 'Password123')
        self.assertTrue(self._is_logged_in())
        memberships_before_count = len(Membership.objects.filter(club = self.club1))
        response = self.client.post(self.url, {'confirmation' : True})
        redirect_url = reverse('member_list', kwargs = {'club_id' : self.club1.id})
        memberships_after_count = len(Membership.objects.filter(club = self.club1))
        self.assertRedirects(response, redirect_url, status_code = 302, target_status_code = 200)
        self.assertEqual(memberships_after_count, memberships_before_count - 1)

    def test_post_kick_member_with_false_form_input(self):
        self.client.login(username = 'test1', password = 'Password123')
        self.assertTrue(self._is_logged_in())
        memberships_before_count = len(Membership.objects.filter(club = self.club1))
        response = self.client.post(self.url, {'confirmation' : False})
        redirect_url = reverse('member_list', kwargs = {'club_id' : self.club1.id})
        memberships_after_count = len(Membership.objects.filter(club = self.club1))
        self.assertRedirects(response, redirect_url, status_code = 302, target_status_code = 200)
        self.assertEqual(memberships_after_count, memberships_before_count)
