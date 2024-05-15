# test_logic.py
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.client = Client()
        cls.client.force_login(cls.author)
        cls.anonymous_client = Client()

    def test_authenticated_user_can_create_note(self):
        response = self.client.post(reverse('notes:add'), {
            'title': 'New note',
            'text': 'New note text',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Note.objects.count(), 1)

    def test_anonymous_user_cannot_create_note(self):
        response = self.anonymous_client.post(reverse('notes:add'), {
            'title': 'New note',
            'text': 'New note text',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Note.objects.count(), 0)

    def test_cannot_create_two_notes_with_same_slug(self):
        self.client.post(reverse('notes:add'), {
            'title': 'New note',
            'text': 'New note text',
            'slug': 'test-slug',
        })
        response = self.client.post(reverse('notes:add'), {
            'title': 'New note 2',
            'text': 'New note text 2',
            'slug': 'test-slug',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'slug', 'Такой slug уже существует, придумайте уникальное значение!')

    def test_slug_is_generated_automatically(self):
        response = self.client.post(reverse('notes:add'), {
            'title': 'New note',
            'text': 'New note text',
        })
        self.assertEqual(response.status_code, 302)
        note = Note.objects.get(title='New note')
        self.assertIsNotNone(note.slug)

    def test_user_can_edit_own_note(self):
        note = Note.objects.create(title='Old note', text='Old note text', author=self.author)
        response = self.client.post(reverse('notes:edit', args=[note.slug]), {
            'title': 'New note',
            'text': 'New note text',
        })
        self.assertEqual(response.status_code, 302)
        note.refresh_from_db()
        self.assertEqual(note.title, 'New note')

    def test_user_cannot_edit_foreign_note(self):
        foreign_author = User.objects.create(username='Foreign author')
        foreign_note = Note.objects.create(title='Foreign note', text='Foreign note text', author=foreign_author)
        response = self.client.post(reverse('notes:edit', args=[foreign_note.slug]), {
            'title': 'New note',
            'text': 'New note text',
        })
        self.assertEqual(response.status_code, 403)

    def test_user_can_delete_own_note(self):
        note = Note.objects.create(title='Old note', text='Old note text', author=self.author)
        response = self.client.post(reverse('notes:delete', args=[note.slug]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cannot_delete_foreign_note(self):
        foreign_author = User.objects.create(username='Foreign author')
        foreign_note = Note.objects.create(title='Foreign note', text='Foreign note text', author=foreign_author)
        response = self.client.post(reverse('notes:delete', args=[foreign_note.slug]))
        self.assertEqual(response.status_code, 403)