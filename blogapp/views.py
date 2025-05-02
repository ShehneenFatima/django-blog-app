# blogapp/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer, UserSerializer
from .permissions import IsAuthorOrReadOnly  # Ensure this is correctly imported

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    # Combine permissions: authenticated to write, author to modify own posts
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]  

    def perform_create(self, serializer):
        # Only reachable if user is authenticated
        serializer.save(author=self.request.user)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')  # ✅ Add ordering
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    def perform_create(self, serializer):
        # Only reachable if user is authenticated
        serializer.save(author=self.request.user)

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]  # Allow unauthenticated registration

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)