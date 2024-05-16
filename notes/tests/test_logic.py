from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from http import HTTPStatus

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.user = User.objects.create(username='Автор')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.form_data = {
            'title': 'Тестовая заметка',
            'text': 'Текст заметки',
            'slug': 'test_note',
            'author': cls.user
        }
        cls.notes = Note.objects.create(
            title='Заметка',
            text='Текст',
            slug='zametka',
            author=cls.user,
        )
        note_url = reverse('notes:detail', args=(cls.notes.slug,))
        cls.url_to_note = note_url
        cls.edit_url = reverse('notes:edit', args=(cls.notes.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.notes.slug,))
        cls.form_data_new = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
            'slug': 'new_slug'
        }

    def test_anonymous_user_cannot_create_note(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_logged_in_user_can_create_note(self):
        response = self.auth_client.post(self.url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_note_creation_slug_uniqueness(self):
        form_data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
            'slug': 'zametka'
        }
        response = self.auth_client.post(reverse('notes:add'), form_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, WARNING)

    def test_slug_is_generated_automatically_if_not_provided(self):
        form_data_no_slug = self.form_data.copy()
        del form_data_no_slug['slug']
        response = self.auth_client.post(self.url, form_data_no_slug)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        note = Note.objects.get(title='Тестовая заметка')
        self.assertIsNotNone(note.slug)

    def test_user_can_edit_own_note(self):
        response = self.auth_client.get(self.edit_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_cannot_edit_foreign_note(self):
        response = self.reader_client.get(self.edit_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_user_can_delete_own_note(self):
        response = self.auth_client.get(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_cannot_delete_foreign_note(self):
        response = self.reader_client.get(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
