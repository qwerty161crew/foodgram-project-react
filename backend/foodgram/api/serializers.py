import webcolors
from rest_framework import serializers
from django.db import models
from rest_framework.generics import get_object_or_404

from recipe.models import Recipe, Tag, Ingredient, FavouritesRecipe, Follow
from users.models import User


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'title', 'count', 'unit')
        model = Ingredient


class TagtSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        fields = ('id', 'title', 'color', 'slug')
        model = Tag


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )
    ingredients = IngredientSerializer(many=True, read_only=True)
    tag = TagtSerializer(many=True, read_only=True)

    class Meta:
        fields = ('id', 'author', 'title', 'image', 'description',
                  'ingredients', 'tag', 'cooking_time', 'pub_date')

        model = Recipe


class FavouritesRecipeSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    recipes = serializers.SlugRelatedField(slug_field='title', read_only=True)

    class Meta:
        field = ('__all__')
        model = FavouritesRecipe

    def validate(self, data):
        if FavouritesRecipe.objects.filter(recipes=self.context['user'].username).exists():
            raise serializers.ValidationError('У вас уже есть этот рецепт')
        if FavouritesRecipe.objects.filter(user=self.context['user']):
            raise serializers.ValidationError('У вас есть этот рецепт')
        return data


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault())
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all())

    def validate(self, data):
        user = get_object_or_404(User, username=data['author'].username)
        follow = Follow.objects.filter(
            user=self.context['request'].user, author=user).exists()
        if user == self.context['request'].user:
            raise serializers.ValidationError(
                'Вы не можете подписаться сам на себя')
        if follow is True:
            raise serializers.ValidationError(
                'Вы уже подписаны на пользователя')
        return data

    class Meta:
        model = Follow
        fields = '__all__'

        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_author'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='prevent_self_follow',
            )
        ]
