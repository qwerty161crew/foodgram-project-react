import base64
import webcolors
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer
from django.core.files.base import ContentFile
from django.db import models
from rest_framework.generics import get_object_or_404
from recipe.models import (Recipe, Tag, Ingredient,
                           FavoritesRecipe,
                           Follow, ShoppingList, IngridientsRecipe)
from django.contrib.auth.models import User


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)


class AmountSerializers(serializers.ModelSerializer):
    class Meta:
        model = IngridientsRecipe
        fields = ('amount', )


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
        fields = ('id', 'title', 'measurement_unit', 'amount')
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
    ingredients = IngredientSerializer(required=True)
    image = Base64ImageField(required=False, allow_null=True)
    amounts = AmountSerializers(required=True)

    class Meta:
        fields = ('__all__')
        model = Recipe

    def validate(self, data):
        if data['amount'] <= 0:
            raise ValueError(
                'убедитесь что количество ингредиентов больше или равно 1')
        if data['ingredients'] is None:
            raise ValueError('должен быть хотябы один ингредиент')
        return data

    def create(self, validated_data):
        # Уберем список достижений из словаря validated_data и сохраним его
        ingredients = validated_data.pop('ingredients')
        amounts = validated_data.pop('amounts')

        # Создадим нового котика пока без достижений, данных нам достаточно
        recipe = Recipe.objects.create(**validated_data)

        # Для каждого достижения из списка достижений
        for ingredient in ingredients:
            # Создадим новую запись или получим существующий экземпляр из БД
            current_ingredient, status = Ingredient.objects.get_or_create(
                **ingredient)
            # Поместим ссылку на каждое достижение во вспомогательную таблицу
            # Не забыв указать к какому котику оно относится
            for amount in amounts:
                IngridientsRecipe.objects.create(
                    ingredient=current_ingredient,
                    recipe=recipe,
                    amount=amount)
        return recipe


class FavouritesRecipeSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    recipe = serializers.SlugRelatedField(slug_field='title', read_only=True)

    class Meta:
        field = ('__all__')
        model = FavoritesRecipe

    def validate(self, data):
        if FavoritesRecipe.objects.filter(
                recipe=self.context['user'].username).exists():
            raise serializers.ValidationError('У вас уже есть этот рецепт')
        if FavoritesRecipe.objects.filter(user=self.context['user']):
            raise serializers.ValidationError(
                'Нельзя добавлять свой рецепт :)')
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
        fields = ('author', 'user', 'recipes')

        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_author'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='prevent_self_author',
            )
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = self.context['request'].user
        recipes = Recipe.objects.filter(author=user)
        data['recipes'] = recipes
        return data


class ShoppingListSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    recipe = serializers.SlugRelatedField(
        slug_field='recipe', many=True, read_only=True)

    class Meta:
        model = ShoppingList
        fields = ('id', 'user', 'recipe')


class AddRecipeInShoppingCart(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username', read_only=True)
    recipe = serializers.SlugRelatedField(
        slug_field='title', queryset=Recipe.objects.all())

    def validate(self, data):
        cart = ShoppingList.objects.filter(
            user=self.context['request'].user,
            recipe__id=self.context['view'].kwargs.get('recipe_id')).exists()
        if cart is True:
            raise serializers.ValidationError(
                'Вы уже добавили рецепт!')
        return data

    class Meta:
        model = ShoppingList
        fields = ('id', 'user', 'recipe')

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe'
            ),
        ]


class ListUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    is_subscribed = serializers.BooleanField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'is_subscribed')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = self.context['request'].user
        follow = Follow.objects.filter(author=user, user=instance).exists()
        count_user = User.objects.all().count()
        data['count'] = count_user
        data['is_subscribed'] = follow
        return data


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class CustomUserSerializer(UserCreateSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')
