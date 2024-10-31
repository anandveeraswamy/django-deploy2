from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Post

class PostModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='12345')
        cls.post = Post.objects.create(
            author=cls.user,
            title='Test Post',
            content='This is a test post'
        )

    def test_post_list_view(self):
        url = reverse('blog-home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This is a test post')
        self.assertTemplateUsed(response, 'blog/home.html')

    def test_post_detail_view(self):
        url = reverse('post-detail', args=[self.post.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)

    def test_create_post_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('post-create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_form.html')

        response = self.client.post(reverse('post-create'), {
            'title': 'New title',
            'content': 'New text',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after POST
        self.assertTrue(Post.objects.filter(title='New title').exists())

    def test_update_post_view(self):
        self.client.login(username='testuser', password='12345')
        url = reverse('post-update', kwargs={'pk': self.post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_form.html')

        response = self.client.post(url, {
            'title': 'Updated title',
            'content': 'Updated text',
        })
        self.post.refresh_from_db()
        self.assertEqual(response.status_code, 302)  # Redirect after POST
        self.assertEqual(self.post.title, 'Updated title')

    def test_delete_post_view(self):
        self.client.login(username='testuser', password='12345')
        url = reverse('post-delete', kwargs={'pk': self.post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_confirm_delete.html')

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Redirect after POST
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())