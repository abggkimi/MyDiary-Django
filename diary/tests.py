import os
import subprocess
import sys
from pathlib import Path

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .models import Comment, Diary


class SecretKeySettingsTests(SimpleTestCase):
    def _run_manage(self, extra_env, *args):
        env = os.environ.copy()
        for name in ('DJANGO_SECRET_KEY', 'DJANGO_DEBUG', 'DJANGO_USE_HTTPS', 'DJANGO_ALLOWED_HOSTS'):
            env.pop(name, None)
        # 子プロセスがプロジェクトの .env を読み直さない。
        env['DJANGO_SKIP_DOTENV'] = 'true'
        env.update(extra_env)
        manage = Path(__file__).resolve().parents[1] / 'manage.py'
        return subprocess.run(
            [sys.executable, str(manage), *args],
            cwd=manage.parent,
            env=env,
            capture_output=True,
            text=True,
        )

    def test_production_without_secret_key_does_not_start(self):
        result = self._run_manage({}, 'check')

        self.assertNotEqual(result.returncode, 0)
        self.assertIn('DJANGO_SECRET_KEY', result.stderr)

    def test_deploy_check_passes_with_secret_key(self):
        result = self._run_manage(
            {'DJANGO_SECRET_KEY': 'deploy-check-Ab3!kQ9mN4pL7wR2vT6yU8zC1dE5fH0x-extra'},
            'check',
            '--deploy',
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('no issues', result.stdout)

    def test_local_debug_starts_without_secret_key(self):
        result = self._run_manage({'DJANGO_DEBUG': 'true'}, 'check')

        self.assertEqual(result.returncode, 0, result.stderr)


class DiaryFlowTests(TestCase):
    password = 'Str0ng-pass-word'

    def setUp(self):
        self.alice = User.objects.create_user('alice', password=self.password)
        self.bob = User.objects.create_user('bob', password=self.password)
        self.public_diary = Diary.objects.create(
            user=self.alice,
            title='公開の日記',
            content='みんなに見せる',
            is_public=True,
        )
        self.private_diary = Diary.objects.create(
            user=self.alice,
            title='非公開の日記',
            content='自分だけ',
            is_public=False,
        )
        Diary.objects.create(
            user=self.bob,
            title='ボブの日記',
            content='ボブの内容',
            is_public=False,
        )

    def test_home_lists_only_public_diaries(self):
        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '公開の日記')
        self.assertNotContains(response, '非公開の日記')
        self.assertNotContains(response, 'ボブの日記')

    def test_diary_list_requires_login(self):
        response = self.client.get(reverse('diary-list'))

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('diary-list')}",
        )

    def test_diary_list_shows_only_own_diaries_and_search(self):
        self.client.force_login(self.alice)

        own_list = self.client.get(reverse('diary-list'))
        self.assertContains(own_list, 'みんなに見せる')
        self.assertContains(own_list, '自分だけ')
        self.assertNotContains(own_list, 'ボブの内容')

        searched = self.client.get(reverse('diary-list'), {'q': '自分だけ'})
        self.assertContains(searched, '自分だけ')
        self.assertNotContains(searched, 'みんなに見せる')
        self.assertNotContains(searched, 'ボブの内容')

    def test_private_detail_is_visible_to_owner_only(self):
        url = reverse('diary-detail', args=[self.private_diary.pk])

        self.assertEqual(self.client.get(url).status_code, 404)

        self.client.force_login(self.bob)
        self.assertEqual(self.client.get(url).status_code, 404)

        self.client.force_login(self.alice)
        self.assertContains(self.client.get(url), '非公開の日記')

    def test_create_diary_belongs_to_logged_in_user(self):
        self.client.force_login(self.alice)

        response = self.client.post(reverse('diary-create'), {
            'title': '新しい日記',
            'content': '本文',
        })

        diary = Diary.objects.get(title='新しい日記')
        self.assertRedirects(response, reverse('diary-list'))
        self.assertEqual(diary.user, self.alice)
        self.assertFalse(diary.is_public)

    def test_other_user_cannot_update_or_delete(self):
        self.client.force_login(self.bob)

        update_url = reverse('diary-update', args=[self.public_diary.pk])
        delete_url = reverse('diary-delete', args=[self.public_diary.pk])

        self.assertEqual(self.client.get(update_url).status_code, 404)
        self.assertEqual(self.client.post(delete_url).status_code, 404)
        self.assertTrue(Diary.objects.filter(pk=self.public_diary.pk).exists())

    def test_comment_on_visible_diary(self):
        self.client.force_login(self.bob)

        response = self.client.post(
            reverse('comment', args=[self.public_diary.pk]),
            {'text': '読みました'},
        )

        self.assertRedirects(response, reverse('diary-detail', args=[self.public_diary.pk]))
        self.assertTrue(
            Comment.objects.filter(
                user=self.bob,
                diary=self.public_diary,
                text='読みました',
            ).exists()
        )
