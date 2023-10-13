from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
from book_clubs.models import User, Club, Membership, Meeting
from book_clubs.tests.helpers import LogInTester, reverse_with_next

class SheduleMeetingTestCase(TestCase, LogInTester):
    """Shedule meeting tests."""

    fixtures = ['book_clubs/tests/fixtures/multiple_memberships.json']

    def setUp(self):
        self.user1 = User.objects.get(id = 1)
        self.club1 = Club.objects.get(id = 1)
        self.club2 = Club.objects.get(id = 2)
        self.membership1 = Membership.objects.get(id = 1)
        self.url = reverse('shedule_meeting', kwargs = {'club_id' : self.club1.id})
        self.form_input = {'deadline' : timezone.now()}

    def test_url(self):
        self.assertEqual(self.url,'/shedule_meeting/1/')

    def test_get(self):
        self.client.login(username = self.user1.username, password = 'Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'shedule_meeting.html')
        form = response.context['meeting_creation_form']
        self.assertFalse(form.is_bound)

    def test_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        response = self.client.get(self.url)
        response_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_club_id_is_invalid(self):
        self.client.login(username=self.user1.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.url = reverse('shedule_meeting', kwargs = {'club_id' : 0})
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('user_club_list'), status_code=302, target_status_code=200)

    def test_user_is_not_member_of_club(self):
        self.client.login(username=self.user1.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.url = reverse('shedule_meeting', kwargs = {'club_id' : self.club2.id})
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('user_club_list'), status_code=302, target_status_code=200)

    def test_user_is_not_owner_of_club(self):
        self.client.login(username=self.user1.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.membership1.member_type = Membership.MemberTypes.MEMBER
        self.membership1.save()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('club_page', kwargs = {'club_id' : self.club1.id}), status_code=302, target_status_code=200)

    def test_post_deadline_crossed(self):
        self.client.login(username=self.user1.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.post(self.url, data = self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shedule_meeting.html')
        form = response.context['meeting_creation_form']
        self.assertTrue(form.is_bound)

    def test_post_valid(self):
        self.client.login(username=self.user1.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        self.form_input['deadline'] = self.form_input['deadline'].replace(year = timezone.now().year + 1)
        self.url = reverse('shedule_meeting', kwargs = {'club_id' : self.club1.id})
        before_meetings_count = Meeting.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_meetings_count = Meeting.objects.count()
        self.assertRedirects(response, reverse('meeting_list', kwargs = {'club_id' : self.club1.id}), status_code=302, target_status_code=200)
        self.assertEqual(after_meetings_count, before_meetings_count + 1)
