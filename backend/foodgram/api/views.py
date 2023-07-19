from rest_framework import viewsets, status, generics, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import get_object_or_404
from rest_framework import filters
from rest_framework.request import Request
from rest_framework.response import Response
import base64
import io
import csv
from django.http import FileResponse, HttpResponse
from reportlab.pdfgen import canvas
from recipe.models import ShoppingList
from django.db.models import Sum

from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User


from recipe.models import Recipe, ShoppingList, Follow, Ingredient
from .pagination import CustomPagination
from .permissions import IsAuthOrReadOnly, IsAdminOrReadOnly
from .serializers import (RecipeSerializer, TagtSerializer,
                          ListUserSerializer, ShoppingListSerializer,
                          ChangePasswordSerializer, CreateUserSerializers,
                          AddRecipeInShoppingCart, FollowSerializer,
                          IngredientSerializer)
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


class ListUserViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
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


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return self.request.user.follower.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FollowSubscriptionsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)


class IngridientsViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthOrReadOnly, )


class FileDownloadListAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        shopping_list = ShoppingList.objects.get(user=request.user)
        recipes = Ingredient.objects.filter(ingredients__recipe=shopping_list)
        response = HttpResponse(
            content_type='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename="somefilename.csv"'},
        )

        for recipe in recipes:
            writer = csv.writer(response)
            writer.writerow([f'{recipe}'])
            # writer.writerow(['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"])

        return response
