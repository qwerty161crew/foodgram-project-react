

import webcolors

from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer
from django.db import models, transaction
from recipe.models import (Recipe, Tag, Ingredient,
                           FavoritesRecipe,
                           Follow, ShoppingList, IngredientsRecipe)
from django.contrib.auth.models import User


class AuthorSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'username')


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
        if data['amount'] < 1:
            raise ValueError(
                'убедитесь что количество ингредиентов больше или равно 1')
        return result


class TagtSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class RecipeSerializer(serializers.ModelSerializer):
    author = AuthorSerializers(required=False)
    ingredients = IngredientInRecipeSerializer(
        many=True, required=True, source='ingredients_in_recipe')
    image = Base64ImageField(required=False, allow_null=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), required=True)

    class Meta:
        fields = ('__all__')
        model = Recipe

    def validate(self, data):
        result = super().validate(data)
        if not data['ingredients_in_recipe']:
            raise serializers.ValidationError(
                'должен быть хотябы один ингредиент')
        list_ingr = [item['id']
                     for item in data['ingredients_in_recipe']]
        all_ingredients, distinct_ingredients = (
            len(list_ingr), len(set(list_ingr)))
        if len(list_ingr) < 1:
            raise serializers.ValidationError('должен минимум один ингредиент')
        if not data['tags']:
            raise serializers.ValidationError('Должен быть минимум один тег')
        if all_ingredients != distinct_ingredients:
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальными')
        if data['cooking_time'] < 1:
            raise serializers.ValidationError(
                'время приготовления должно состовлять минимум минуту')

        return result

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients_in_recipe')
        tags = validated_data.pop('tags')
        validated_data['author'] = self.context['request'].user
        recipe = Recipe.objects.create(
            **validated_data)
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
                'measurement_unit':
                ingredient_in_recipe.ingredient.measurement_unit,
                'name': ingredient_in_recipe.ingredient.name
            }
            result.append(entry)

        data['ingredients'] = result
        return data


class FollowSerializer(serializers.ModelSerializer):

    def validate(self, data):
        print(data, self.context, self.instance)
        user = data.user
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
        fields = ()

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

    def create(self, validated_data):
        author = self.context['view'].kwargs['user_id']
        follow = Follow.objects.create(user=self.context['request'].user,
                                       author=author).save()
        return follow

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = self.context['request'].user
        recipes = Recipe.objects.filter(author=user)
        data['recipes'] = recipes
        return data


class ListUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    is_subscribed = serializers.BooleanField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'is_subscribed')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = self.context['request'].user
        if user.is_authenticated:
            follow = Follow.objects.filter(author=instance, user=user).exists()
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
    tags = TagtSerializer(many=True, read_only=True)

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


class UserWithRecipes(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        queryset = Recipe.objects.filter(author=instance)
        serializers = RecipeSerializer(queryset, many=True)
        recipes_count = Recipe.objects.filter(author=instance).count()
        is_subscribed = Follow.objects.filter(
            user=self.context['request'].user, author=instance).exists()
        data['recipes'] = serializers.data
        data['recipes_count'] = recipes_count
        data['is_subscribed'] = is_subscribed
        return data


class UserSubscriptions(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        recipes = Recipe.objects.filter(author=instance)
        serializer = RecipeSerializer(recipes, many=True)
        recipes_count = Recipe.objects.filter(author=instance).count()
        is_subscribed = Follow.objects.filter(
            user=self.context['request'].user,
            author__username=instance).exists()

        data['recipes'] = serializer.data
        data['recipes_count'] = recipes_count
        data['is_subscribed'] = is_subscribed
        return data


class RecipeMinified(serializers.ModelSerializer):
    image = Base64ImageField(required=True, allow_null=True)
    tags = TagtSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'image', 'name', 'cooking_time', 'tags')


class FavoriteRecipeSerializers(serializers.ModelSerializer):

    class Meta:
        model = FavoritesRecipe
        fields = ()

    def validate(self, data):
        if FavoritesRecipe.objects.filter(
                recipe=self.context['user'].username).exists():
            raise serializers.ValidationError('У вас уже есть этот рецепт')
        if FavoritesRecipe.objects.filter(user=self.context['user']):
            raise serializers.ValidationError(
                'Нельзя добавлять свой рецепт :)')
        return data

    def to_representation(self, instance):
        print(instance)
        data = super().to_representation(instance)
        recipes = Recipe.objects.filter(is_favorited__in=instance)
        print(recipes)
        serializers = RecipeMinified(recipes, context=self.context, many=True)

        data['recipes'] = serializers.data
        return data


class ShoppingListSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingList
        fields = ()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        recipes = Recipe.objects.filter(is_in_shopping_cart__in=instance)
        serializers = RecipeMinified(recipes, context=self.context)

        data['recipes'] = serializers.data
        return data


class RecipeNotAuthenticated(serializers.ModelSerializer):
    author = AuthorSerializers(required=False)
    ingredients = IngredientInRecipeSerializer(
        many=True, required=True, source='ingredients_in_recipe')
    image = Base64ImageField(required=False, allow_null=True)
    tags = TagtSerializer(many=True, read_only=True)

    class Meta:
        fields = ('__all__')
        model = Recipe
