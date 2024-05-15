from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse_lazy

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.test_note = Note.objects.create(
            title='Заголовок со слагом', text='Текст', author=cls.author,
            slug='test'
        )

    def test_anonymous_access(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse_lazy(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authenticated_access(self):
        self.client.force_login(self.author)
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:done', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse_lazy(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_owner_access(self):
        self.client.force_login(self.author)
        urls = (
            ('notes:detail', self.test_note.slug),
            ('notes:edit', self.test_note.slug),
            ('notes:delete', self.test_note.slug),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse_lazy(name, args=(args,))
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_non_owner_access(self):
        self.client.force_login(self.reader)
        urls = (
            ('notes:detail', self.test_note.slug),
            ('notes:edit', self.test_note.slug),
            ('notes:delete', self.test_note.slug),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse_lazy(name, args=(args,))
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_anonymous_redirect(self):
        login_url = reverse_lazy('users:login')
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:done', None),
            ('notes:detail', self.test_note.slug),
            ('notes:edit', self.test_note.slug),
            ('notes:delete', self.test_note.slug),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse_lazy(name, args=(args,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
