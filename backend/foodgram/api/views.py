
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
from foodgram.utils import download
from django.contrib.auth.models import User
from django.db.models import Sum

from recipe.models import (Recipe, ShoppingList, Follow,
                           Ingredient, Tag, FavoritesRecipe,
                           IngredientsRecipe)

from .serializers import (RecipeSerializer, TagtSerializer,
                          ListUserSerializer, ShoppingListSerializer,
                          CustomUserSerializer, FollowSerializer,
                          IngredientsSerializers, RecipeListSerializers,
                          UserWithRecipes, UserSubscriptions,
                          FavoriteRecipeSerializers,
                          RecipeNotAuthenticated
                          )
from .filters import RecipeFilter


class RecipeViewset(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if not self.request.user.is_authenticated:
            return RecipeNotAuthenticated
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializers
        return RecipeSerializer

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    @action(detail=True, methods=['POST', 'DELETE'])
    def favorite(self, request, *args, **kwargs):
        user = request.user
        recipe_id = self.get_object()
        context = self.get_serializer_context()
        if request.method == 'POST':
            if (FavoritesRecipe.objects.filter(user=user,
                                               recipe=recipe_id).exists()):
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'errors': 'вы уже добавили этот рецепт'})
            FavoritesRecipe.objects.create(user=user, recipe=recipe_id)
            favorite_recipes = FavoritesRecipe.objects.filter(user=user)

            serializers = FavoriteRecipeSerializers(
                favorite_recipes)
            return Response(status=status.HTTP_201_CREATED,
                            data=serializers.data)
        if request.method == 'DELETE':
            if not (FavoritesRecipe.objects.filter(user=user,
                                                   recipe=recipe_id).exists()):
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'errors': 'У вас нет этого рецепта'})
            FavoritesRecipe.objects.filter(
                user=user, recipe=recipe_id).delete()
            favorite_recipes = FavoritesRecipe.objects.filter(user=user)

            serializers = FavoriteRecipeSerializers(
                favorite_recipes, context=context)
            return Response(status=status.HTTP_204_NO_CONTENT,
                            data=serializers.data)

    @action(detail=True, methods=['POST', 'DELETE'])
    def shopping_cart(self, request, *args, **kwargs):
        user = request.user
        recipe_id = self.get_object()
        context = self.get_serializer_context()
        if request.method == 'POST':
            if ShoppingList.objects.filter(user=user, recipe=recipe_id):
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'errors': 'вы уже добавили этот рецепт'})
            ShoppingList.objects.create(user=user, recipe=recipe_id)
            recipe_in_cart = ShoppingList.objects.filter(user=user)
            serializers = ShoppingListSerializer(
                recipe_in_cart, context=context, many=True)
            return Response(status=status.HTTP_201_CREATED,
                            data=serializers.data)
        if request.method == 'DELETE':
            ShoppingList.objects.filter(user=user, recipe=recipe_id).delete()
            recipe_in_cart = ShoppingList.objects.filter(user=user)
            serializers = ShoppingListSerializer(
                recipe_in_cart, context=context, many=True)
            return Response(status=status.HTTP_204_NO_CONTENT,
                            data=serializers.data)

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        shopping_lists = ShoppingList.objects.filter(user=request.user)
        recepies = Recipe.objects.filter(
            is_in_shopping_cart__in=shopping_lists)
        ingredient_receipes = IngredientsRecipe.objects.filter(
            recipe__in=recepies
        ).values('ingredient').annotate(total_amount=Sum('amount'))
        return download(ingredient_receipes)


class TagViewset(mixins.RetrieveModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagtSerializer
    permission_classes = (AllowAny, )
    pagination_class = None


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

    @action(detail=True, methods=['POST', 'DELETE'])
    def subscribe(self, request, *args, **kwargs):
        author = self.get_object()
        user = request.user
        context = super().get_serializer_context()
        if request.method == 'POST':
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
        if request.method == 'DELETE':
            Follow.objects.filter(user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'])
    def subscriptions(self, request, *args, **kwargs):
        user = request.user
        follows = Follow.objects.filter(user=user)
        users = User.objects.filter(following__in=follows)
        paginator = PageNumberPagination()
        results = paginator.paginate_queryset(users, request)
        context = self.get_serializer_context()
        serializer = UserWithRecipes(
            results, context=context, many=True)
        # serializer.is_valid()
        return paginator.get_paginated_response(serializer.data)
