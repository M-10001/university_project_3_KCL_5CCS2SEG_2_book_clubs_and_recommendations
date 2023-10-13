from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from book_clubs.forms import SignUpForm
from book_clubs.models import User
from book_clubs.tests.helpers import LogInTester

class SignUpViewTestCase(TestCase,LogInTester):


    def setUp(self):
        self.url = reverse('sign_up')
        self.form_input = {
            'first_name': 'test1_f',
            'last_name': 'test1_l',
            'username': 'test1',
            'email': 'test1@gmail.com',
            'new_password': 'Password123',
            'password_confirmation': 'Password123'
            }


    def test_sign_up_url(self):
        self.assertEqual(self.url,'/sign_up/')

    def test_get_sign_up(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertFalse(form.is_bound)

    def test_unsuccesful_sign_up(self):
       self.form_input['username'] = 'te'
       before_count = User.objects.count()
       response = self.client.post(self.url, self.form_input)
       after_count = User.objects.count()
       self.assertEqual(after_count, before_count)
       self.assertEqual(response.status_code, 200)
       self.assertTemplateUsed(response, 'sign_up.html')
       form = response.context['form']
       self.assertTrue(isinstance(form, SignUpForm))
       self.assertTrue(form.is_bound)
       self.assertFalse(self._is_logged_in())

    def test_succesful_sign_up(self):
       before_count = User.objects.count()
       response = self.client.post(self.url, self.form_input, follow=True)
       after_count = User.objects.count()
       self.assertEqual(after_count, before_count + 1)
       user = User.objects.get(username = 'test1')
       response_url = reverse('user_page')
       self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
       self.assertTemplateUsed(response, 'user_page.html')
       self.assertEqual(user.first_name, 'test1_f')
       self.assertEqual(user.last_name, 'test1_l')
       self.assertEqual(user.email, 'test1@gmail.com')
       is_password_correct = check_password('Password123', user.password)
       self.assertTrue(is_password_correct)
       self.assertTrue(self._is_logged_in())
