from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse, reverse_lazy

from http import HTTPStatus

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

    def test_home_page_accessible_to_anonymous(self):
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_notes_list_accessible_to_authenticated_user(self):
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_detail_accessible_to_author(self):
        self.client.force_login(self.author)
        url = reverse('notes:detail', args=(self.test_note.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_edit_and_delete_accessible_to_author(self):
        self.client.force_login(self.author)
        urls = (
            ('notes:edit', (self.test_note.slug,)),
            ('notes:delete', (self.test_note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_edit_and_delete_inaccessible_to_non_author(self):
        self.client.force_login(self.reader)
        urls = (
            ('notes:edit', (self.test_note.slug,)),
            ('notes:delete', (self.test_note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse_lazy('users:login')
        for name in ('notes:edit', 'notes:delete', 'notes:add', 'notes:list'):
            with self.subTest(name=name):
                if name in ('notes:edit', 'notes:delete'):
                    url = reverse_lazy(name, args=(self.test_note.slug,))
                else:
                    url = reverse_lazy(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
                self.client.logout()
