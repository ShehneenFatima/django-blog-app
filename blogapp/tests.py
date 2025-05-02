# blogapp/tests.py
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import Post, Comment

class BlogAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        response = self.client.post('/api/token/', {'username': 'testuser', 'password': 'testpass123'})
        self.token = response.data['access']

    def test_create_post(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post('/api/posts/', {'title': 'Test Post', 'content': 'Hello World'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unauthorized_create_post(self):
        response = self.client.post('/api/posts/', {'title': 'No Auth', 'content': 'Should Fail'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_post(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        post = Post.objects.create(title='Old Title', content='Old Content', author=self.user)
        response = self.client.put(f'/api/posts/{post.id}/', {'title': 'New Title', 'content': 'New Content'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'New Title')

    def test_delete_post(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        post = Post.objects.create(title='To Delete', content='Delete Me', author=self.user)
        response = self.client.delete(f'/api/posts/{post.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_comment(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        post = Post.objects.create(title='Test Post', content='Hello World', author=self.user)
        response = self.client.post('/api/comments/', {'post': post.id, 'text': 'Great post!'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)