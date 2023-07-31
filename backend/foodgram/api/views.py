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
                          IsNotAuthenticated, IsAuthorOrReadOnly, IsAdminOrReadOnly)
from .serializers import (RecipeSerializer, TagtSerializer,
                          ListUserSerializer, ShoppingListSerializer,
                          ChangePasswordSerializer, CustomUserSerializer,
                          AddRecipeInShoppingCart, FollowSerializer,
                          IngredientsInRecipeSerializers, RecipeListSerializers)
from .filters import RecipeFilter


class RecipeViewset(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly, IsAuthOrReadOnly)
    filterset_class = RecipeFilter
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializers
        return RecipeSerializer

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


class FollowViewSet(mixins.CreateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated, )
    # lookup_field = 'pk'

    # def get_user(self):
    #     return get_object_or_404(User, user=self.get_object('id'))

    def destroy(self, request, pk=None):
        author_id = self.request.parser_context['kwargs'].get('id')
        author = get_object_or_404(User, id=author_id)
        print(author)
        self.serializer.delete(user=self.request.user, author=author)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        return self.request.user.follower.all()

    def perform_create(self, serializer):
        author_id = self.request.parser_context['kwargs'].get('id')
        author = get_object_or_404(User, id=author_id)
        print(author)
        serializer.save(user=self.request.user, author=author)


class FollowSubscriptionsViewSet(mixins.ListModelMixin,
                                 viewsets.GenericViewSet):
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class IngridientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsInRecipeSerializers
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrReadOnly, )


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

    # def get_permissions(self):
    #     return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ListUserSerializer
        return CustomUserSerializer
