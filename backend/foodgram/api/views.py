from rest_framework import viewsets, status, generics, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed

from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import get_object_or_404

from rest_framework.request import Request
from rest_framework.response import Response


from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User


from recipe.models import Recipe, ShoppingList
from .pagination import CustomPagination
from .permissions import IsAuthOrReadOnly, IsAdminOrReadOnly
from .serializers import RecipeSerializer, TagtSerializer, ListUserSerializer, ShoppingListSerializer, ChangePasswordSerializer, CreateUserSerializers, AddRecipeInShoppingCart
from .filters import RecipeFilter


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


class ListUserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = ListUserSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminUser, )


class ShoppingListViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = ShoppingListSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return ShoppingList.objects.filter(user_id=self.request.user.id)


class AddRecipeInShoppingCart(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = AddRecipeInShoppingCart
    permission_classes = (IsAuthenticated, )

    def get_recipe(self):
        return get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))

    def get_queryset(self):
        return self.get_recipe()

    def perform_create(self, serializer) -> None:
        serializer.save(user=self.request.user, recipe=self.get_recipe())


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
    serializer_class = CreateUserSerializers
