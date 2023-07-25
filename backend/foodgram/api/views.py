import io

from djoser.views import UserViewSet
from django.http import FileResponse
from reportlab.pdfgen import canvas
from rest_framework import viewsets, status, mixins, generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from django.http import FileResponse, HttpResponse
from rest_framework.pagination import LimitOffsetPagination


from django.contrib.auth.models import User

from recipe.models import Recipe, ShoppingList, Follow, Ingredient

from .permissions import (IsAuthOrReadOnly,
                          IsAdminOrReadOnly,
                          IsNotAuthenticated, IsAuthorOrReadOnly)
from .serializers import (RecipeSerializer, TagtSerializer,
                          ListUserSerializer, ShoppingListSerializer,
                          ChangePasswordSerializer, CustomUserSerializer,
                          AddRecipeInShoppingCart, FollowSerializer,
                          IngredientSerializer)
from .filters import RecipeFilter


class RecipeViewset(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly, IsAuthOrReadOnly)
    filterset_class = RecipeFilter
    pagination_class = LimitOffsetPagination

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


class ShoppingListViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    serializer_class = ShoppingListSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return ShoppingList.objects.filter(user_id=self.request.user.id)


class AddRecipeInShoppingCart(mixins.CreateModelMixin,
                              viewsets.GenericViewSet):
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


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return self.request.user.follower.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FollowSubscriptionsViewSet(mixins.ListModelMixin,
                                 viewsets.GenericViewSet):
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class IngridientsViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthOrReadOnly, )

    permission_classes = (IsAuthenticated, )


class FileDownloadListAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        shopping_list = ShoppingList.objects.get(user=request.user)
        recipes = Ingredient.objects.filter(
            ingredients__is_in_shopping_cart=shopping_list)
        buffer = io.BytesIO()
        for ingredients in recipes:
            p = canvas.Canvas(buffer)

            p.drawString(
                50, 50, f"{ingredients.title, ingredients.count, ingredients.unit}"
            )

            p.showPage()
            p.save()

            buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename="hello.pdf")


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer
