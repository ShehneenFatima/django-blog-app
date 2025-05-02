from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from blogapp.models import Post, Comment

class BlogAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        # Create test user
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        # Get JWT token
        response = self.client.post('/api/token/', {'username': 'testuser', 'password': 'testpass123'})
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    # POST Tests 
    def test_create_post(self):
        response = self.client.post('/api/posts/', {'title': 'Test Post', 'content': 'Hello World'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)

    def test_unauthorized_create_post(self):
        self.client.credentials()  # Clear auth
        response = self.client.post('/api/posts/', {'title': 'No Auth', 'content': 'Fail'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_post_invalid_data(self):
        response = self.client.post('/api/posts/', {'title': '', 'content': ''})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # GET Tests 
    def test_list_posts(self):
        Post.objects.create(title='Test 1', content='Content 1', author=self.user)
        Post.objects.create(title='Test 2', content='Content 2', author=self.user)
        response = self.client.get('/api/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_retrieve_post(self):
        post = Post.objects.create(title='Detail Test', content='Detail Content', author=self.user)
        response = self.client.get(f'/api/posts/{post.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Detail Test')

    # PUT Tests 
    def test_update_post(self):
        post = Post.objects.create(title='Old Title', content='Old Content', author=self.user)
        response = self.client.put(f'/api/posts/{post.id}/', {'title': 'New Title', 'content': 'New Content'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(post.title, 'New Title')

    def test_update_other_users_post(self):
        other_user = User.objects.create_user(username='other', password='otherpass123')
        post = Post.objects.create(title='Other Post', content='Other Content', author=other_user)
        response = self.client.put(f'/api/posts/{post.id}/', {'title': 'Hacked!', 'content': 'Hacked'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # DELETE Test
    def test_delete_post(self):
        post = Post.objects.create(title='ToDelete', content='Delete Me', author=self.user)
        response = self.client.delete(f'/api/posts/{post.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 0)

    def test_delete_other_users_post(self):
        other_user = User.objects.create_user(username='other', password='otherpass123')
        post = Post.objects.create(title='Other Post', content='Other Content', author=other_user)
        response = self.client.delete(f'/api/posts/{post.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    #  Comment Tests 
    def test_create_comment(self):
        post = Post.objects.create(title='Test Post', content='Hello World', author=self.user)
        response = self.client.post('/api/comments/', {'post': post.id, 'text': 'Great post!'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_comment_invalid_post_id(self):
        response = self.client.post('/api/comments/', {'post': 99999, 'text': 'Invalid post ID'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_comments_for_post(self):
        post = Post.objects.create(title='Test Post', content='Hello World', author=self.user)
        Comment.objects.create(post=post, text='First!', author=self.user)
        Comment.objects.create(post=post, text='Second!', author=self.user)
        response = self.client.get(f'/api/comments/?post={post.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    # Auth Tests
    def test_register_user(self):
        response = self.client.post('/api/register/', {'username': 'newuser', 'password': 'newpass123'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_jwt_login(self):
        response = self.client.post('/api/token/', {'username': 'testuser', 'password': 'testpass123'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_jwt_refresh(self):
        refresh_token = self.client.post('/api/token/', {'username': 'testuser', 'password': 'testpass123'}).data['refresh']
        response = self.client.post('/api/token/refresh/', {'refresh': refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)