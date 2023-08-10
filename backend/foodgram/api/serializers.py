import base64
import webcolors
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, TokenCreateSerializer
from django.core.files.base import ContentFile
from django.db import models, transaction
from rest_framework.generics import get_object_or_404
from recipe.models import (Recipe, Tag, Ingredient,
                           FavoritesRecipe,
                           Follow, ShoppingList, IngredientsRecipe)
from django.contrib.auth.models import User


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ModelField(
        model_field=IngredientsRecipe()._meta.get_field('id'))

    class Meta:
        fields = ('id', 'amount', )
        model = IngredientsRecipe

    def validate(self, data):
        result = super().validate(data)
        if data['amount'] <= 0:
            raise ValueError(
                'убедитесь что количество ингредиентов больше или равно 1')
        return result


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
    ingredients = IngredientInRecipeSerializer(
        many=True, required=True, source='ingredients_in_recipe')
    image = Base64ImageField(required=True, allow_null=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())

    class Meta:
        fields = ('__all__')
        model = Recipe

    def validate(self, data):
        result = super().validate(data)
        if not data['ingredients_in_recipe']:
            raise ValueError('должен быть хотябы один ингредиент')
        return result

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients_in_recipe')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            IngredientsRecipe.objects.create(
                ingredient_id=ingredient['id'],
                recipe_id=recipe.id,
                amount=ingredient['amount']).save()
        recipe.tags.set(tags)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):

        ingredients = validated_data.pop('ingredients_in_recipe')
        tags = validated_data.pop('tags')
        instance.ingredients_in_recipe.all().delete()
        for ingredient in ingredients:
            IngredientsRecipe.objects.create(
                ingredient_id=ingredient['id'],
                recipe_id=instance.id,
                amount=ingredient['amount']).save()
        instance.tags.set(tags)
        instance = super().update(instance, validated_data)
        return instance

    def to_representation(self, instance):
        result = []
        data = super().to_representation(instance)
        ingredients = IngredientsRecipe.objects.filter(recipe=instance)
        for ingredient_in_recipe in ingredients:
            entry = {
                'id': ingredient_in_recipe.ingredient.id,
                'amount': ingredient_in_recipe.amount,
                'measurement_unit': ingredient_in_recipe.ingredient.measurement_unit,
                'name': ingredient_in_recipe.ingredient.name
            }
            result.append(entry)

        data['ingredients'] = result
        return data


class FavouritesRecipeSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    recipe = serializers.SlugRelatedField(slug_field='name', read_only=True)

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
    # author = serializers.SlugRelatedField(
    #     slug_field='username',
    #     queryset=User.objects.all())

    def validate(self, data):
        print(data, self.context, self.instance)
        user = get_object_or_404(User, id=self.context['view'].kwargs['id'])
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
        fields = ('user', )
        # lookup_field = 'pk'

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
        slug_field='name', queryset=Recipe.objects.all())

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
        data['is_subscribed'] = follow
        return data


class CustomUserSerializer(UserCreateSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')

    def validate(self, data):
        print(data)
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError(
                'Эта почта уже используется другим пользователем')
        return data


class IngredientsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('__all__')


class RecipeListSerializers(RecipeSerializer):

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = self.context['request'].user
        recipe_id = Recipe.objects.get(id=data['id'])
        is_favorited = FavoritesRecipe.objects.filter(
            recipe=recipe_id, user=user).exists()
        is_in_shopping_cart = ShoppingList.objects.filter(
            recipe=recipe_id, user=user).exists()
        data['is_favorited'] = is_favorited
        data['is_in_shopping_cart'] = is_in_shopping_cart

        return data
