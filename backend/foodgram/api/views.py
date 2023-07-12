from rest_framework import viewsets, status, generics, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from django.conf import settings
from django.core.mail import send_mail
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import action

from .pagination import CustomPagination
from .permissions import IsAuthOrReadOnly, IsAdminOrReadOnly
from .serializers import RecipeSerializer, TagtSerializer, ListUserSerializer, ShoppingListSerializer, ChangePasswordSerializer
from .filters import RecipeFilter
from rest_framework.request import Request
from rest_framework.response import Response
from recipe.models import Recipe, ShoppingList
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
    serializer_class = ListUserSerializer
    permission_classes = (IsAdminUser, )


class ShoppingListViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingListSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        user = self.request.user
        return ShoppingList.objects.filter(user=user.username)


class ChangePasswordViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated, )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(status=status.HTTP_204_NO_CONTENT, headers=headers)

    def perform_create(self, serializer):
        user = self.request.user
        user.set_password(raw_password=serializer.validated_data['password'])
        user.save()


class CreateUserViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    pass