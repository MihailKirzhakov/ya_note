from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestNote(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            username='tester1', password='password1'
        )
        cls.user2 = User.objects.create_user(
            username='tester2', password='password2'
        )
        cls.note1 = Note.objects.create(
            title='Тестовая заметка 1',
            text='Тестовый текст 1',
            author=cls.user1
        )
        cls.note2 = Note.objects.create(
            title='Тестовая заметка 2',
            text='Тестовый текст 2',
            author=cls.user2
        )

    def test_note_list_view(self):
        self.client.login(username='tester1', password='password1')
        response = self.client.get(reverse('notes:list'))
        self.assertIn('object_list', response.context)
        self.assertEqual(len(response.context['object_list']), 1)
        self.assertEqual(response.context['object_list'][0], self.note1)

    def test_note_list_view_other_user(self):
        self.client.login(username='tester2', password='password2')
        response = self.client.get(reverse('notes:list'))
        self.assertIn('object_list', response.context)
        self.assertEqual(len(response.context['object_list']), 1)
        self.assertEqual(response.context['object_list'][0], self.note2)

    def test_note_create_view(self):
        self.client.login(username='tester1', password='password1')
        response = self.client.get(reverse('notes:add'))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_note_update_view(self):
        self.client.login(username='tester1', password='password1')
        response = self.client.get(
            reverse('notes:edit', args=[self.note1.slug])
        )
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_note_detail_view(self):
        self.client.login(username='tester1', password='password1')
        response = self.client.get(
            reverse('notes:detail', args=[self.note1.slug])
        )
        self.assertIn('object', response.context)
        self.assertEqual(response.context['object'], self.note1)
