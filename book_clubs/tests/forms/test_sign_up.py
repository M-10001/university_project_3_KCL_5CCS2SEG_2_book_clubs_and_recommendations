from django.contrib.auth.hashers import check_password
from django import forms
from django.test import TestCase
from book_clubs.forms import SignUpForm
from book_clubs.models import User

class SignUpFormTestCase(TestCase):

    def setUp(self):
        self.form_input = {
            'first_name' : 'Mark',
            'last_name' : 'Sparrow',
            'age' : 18,
            'username' : 'marksparrow',
            'email' : 'marksparrow@gmail.com',
            'location' : 'London',
            'new_password' : 'Password123',
            'password_confirmation' : 'Password123'
            }


    def test_valid_sign_up_form(self):
        form = SignUpForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = SignUpForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('age', form.fields)
        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)
        self.assertIn('location', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))
        self.assertIn('new_password', form.fields)
        new_password_widget= form.fields['new_password'].widget
        self.assertTrue(isinstance(new_password_widget, forms.PasswordInput))
        self.assertIn('password_confirmation', form.fields)
        passord_confirmation_widget= form.fields['password_confirmation'].widget
        self.assertTrue(isinstance(passord_confirmation_widget, forms.PasswordInput))

    def test_form_uses_model_validation(self):
        self.form_input['username'] = 'badusername'
        form = SignUpForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_password_must_contain_uppercase_character(self):
        self.form_input['password'] = 'password123'
        self.form_input['password_confirmation'] = 'password123'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_lowercase_character(self):
        self.form_input['new_password'] = 'PASSWORD123'
        self.form_input['password_confirmation'] = 'PASSWORD123'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_number(self):
        self.form_input['new_password'] = 'Passwordabc'
        self.form_input['password_confirmation'] = 'Passwordabc'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_new_password_and_password_confirmation_are_identical(self):
        self.form_input['password_confirmation'] = 'WrongPassword123'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = SignUpForm(data=self.form_input)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count+1)
        user = User.objects.get(username='marksparrow')
        self.assertEqual(user.first_name, 'Mark')
        self.assertEqual(user.last_name, 'Sparrow')
        self.assertEqual(user.age, 18)
        self.assertEqual(user.email, 'marksparrow@gmail.com')
        self.assertEqual(user.location, 'London')
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)
