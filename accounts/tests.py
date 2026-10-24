from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AccountFlowTests(TestCase):
    password = 'Str0ng-pass-word'

    def test_signup_creates_user_and_redirects_home(self):
        response = self.client.post(reverse('accounts:signup'), {
            'username': 'newuser',
            'password1': self.password,
            'password2': self.password,
        })

        self.assertRedirects(response, reverse('index'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_redirects_home(self):
        User.objects.create_user('alice', password=self.password)

        response = self.client.post(reverse('accounts:login'), {
            'username': 'alice',
            'password': self.password,
        })

        self.assertRedirects(response, reverse('index'))

    def test_login_rejects_wrong_password(self):
        User.objects.create_user('alice', password=self.password)

        response = self.client.post(reverse('accounts:login'), {
            'username': 'alice',
            'password': 'wrong-password',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ログイン')
