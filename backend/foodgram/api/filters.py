from django_filters import rest_framework as filter_

from recipe.models import Recipe


class RecipeFilter(filter_.FilterSet):
    tag = filter_.CharFilter(field_name='tag__title', lookup_expr='exact')
    author = filter_.NumberFilter(
        field_name='author', lookup_expr='exact')
    favorite_recipe = filter_.BooleanFilter(
        'is_favorited', lookup_expr='exact')
    shopping_cart = filter_.BooleanFilter(
        'is_in_shopping_cart', lookup_expr='exact')

    class Meta:
        model = Recipe
        fields = ('author', 'name',
                  'tag')
