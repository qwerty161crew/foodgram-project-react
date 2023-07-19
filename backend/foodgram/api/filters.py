from django_filters import rest_framework as filter_

from recipe.models import Recipe, FavoritesRecipe


class RecipeFilter(filter_.FilterSet):
    tag = filter_.CharFilter(field_name='tag__title', lookup_expr='exact')
    author = filter_.CharFilter(
        field_name='author__username', lookup_expr='exact')
    favorite_recipe = filter_.BooleanFilter(
        'recipes_fovorite', lookup_expr='exact')
    shopping_cart = filter_.BooleanFilter('recipe_cart', lookup_expr='exact')

    class Meta:
        model = Recipe
        fields = ('author', 'title',
                  'ingredients', 'tag')


# class FavoriteRecipeFilter(filter_.FilterSet):
#     shopping_cart = filter_.BooleanFilter(
#         field_name='recipe', lookup_expr='exact')

#     class Meta:
#         model = FavoritesRecipe
#         fields = ('recipe', )
