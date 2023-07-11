from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from django.conf import settings
from django.core.mail import send_mail

from .pagination import CustomPagination
from .permissions import IsAuthOrReadOnly, IsAdminOrReadOnly
from .serializers import RecipeSerializer, TagtSerializer, UserSerializer
from .filters import RecipeFilter
from rest_framework.request import Request
from rest_framework.response import Response
from recipe.models import Recipe
from django.contrib.auth.models import User


class RecipeViewset(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthOrReadOnly, )
    filterset_class = RecipeFilter
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)


class TagViewset(viewsets.ModelViewSet):
    serializer_class = TagtSerializer
    permission_classes = IsAdminOrReadOnly


class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
