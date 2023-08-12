
from djoser.views import UserViewSet

from rest_framework.decorators import action
from rest_framework import viewsets, status, mixins
from rest_framework.permissions import (IsAdminUser, IsAuthenticated,
                                        AllowAny, IsAuthenticatedOrReadOnly)
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
import django_filters.rest_framework
from django.db.utils import IntegrityError

from django.contrib.auth.models import User

from recipe.models import Recipe, ShoppingList, Follow, Ingredient, Tag, FavoritesRecipe

from .serializers import (RecipeSerializer, TagtSerializer,
                          ListUserSerializer, ShoppingListSerializer,
                          CustomUserSerializer,
                          AddRecipeInShoppingCart, FollowSerializer,
                          IngredientsSerializers, RecipeListSerializers,
                          UserWithRecipes, UserSubscriptions
                          )
from .filters import RecipeFilter


class RecipeViewset(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializers
        return RecipeSerializer

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    @action(detail=True, methods=['POST'])
    def favorite(self, request, *args, **kwargs):
        user = request.user
        recipe_id = self.get_object()
        context = self.get_serializer_context()
        if FavoritesRecipe.objects.filter(user=user, recipe=recipe_id).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': 'вы уже добавили этот рецепт'})
        FavoritesRecipe.objects.create(user=user, recipe=recipe_id)
        serializers = RecipeListSerializers(instance=recipe_id, context=context)
        return Response(status=status.HTTP_201_CREATED, data=serializers.data)


class TagViewset(mixins.RetrieveModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagtSerializer
    permission_classes = (AllowAny, )
    pagination_class = None

    # def get_object(self):
    #     queryset = get_object_or_404(Tag, id=self.kwargs.get('pk'))
    #     return queryset


class ListUserViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = ListUserSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminUser, )


class FollowViewSet(mixins.CreateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated, )
    lookup_field = 'user_id'

    def get_queryset(self):
        return self.request.user.follower.all()

    def perform_create(self, serializer):
        author_id = self.get_object()
        author = get_object_or_404(User, id=author_id)

        return serializer.save(user=self.request.user, author=author)


class IngridientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializers
    pagination_class = None
    permission_classes = (AllowAny, )
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination
    permission_classes = (AllowAny, )

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ListUserSerializer
        return CustomUserSerializer

    @action(detail=True, methods=['POST'])
    def subscribe(self, request, *args, **kwargs):
        author = self.get_object()
        user = request.user
        context = super().get_serializer_context()
        if author.id == user.id:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'errors':
                                  'Вы не можете подписаться на самого себя'})
        try:
            Follow.objects.create(user=user, author=author)
        except IntegrityError:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'errors':
                                  'вы уже подписаны на данного пользователя'})
        serializer = UserWithRecipes(instance=author, context=context)

        return Response(status=status.HTTP_201_CREATED, data=serializer.data)

    @action(detail=False, methods=['GET'])
    def subscriptions(self, request, *args, **kwargs):
        user = request.user
        context = self.get_serializer_context()
        serializer = UserSubscriptions(instance=user, context=context)
        # serializer.is_valid()
        return Response(status=status.HTTP_200_OK, data=serializer.data)
