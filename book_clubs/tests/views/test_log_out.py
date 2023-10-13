from django.test import TestCase
from django.urls import reverse
from book_clubs.forms import User
from book_clubs.tests.helpers import LogInTester, reverse_with_next

class LogOutViewTestCase(TestCase, LogInTester):

    fixtures = ['book_clubs/tests/fixtures/single_user.json']

    def setUp(self):
        self.url = reverse('log_out')
        self.user = User.objects.get(id = 1)

    def test_log_out_url(self):
        self.assertEqual(self.url,'/log_out/')

    def test_get_log_out(self):
        self.client.login(username='test1', password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)
        response_url = reverse('home')
        self.assertRedirects(response,response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertFalse(self._is_logged_in())

    def test_get_log_out_without_being_logged_in(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'log_in.html')
        self.assertFalse(self._is_logged_in())
