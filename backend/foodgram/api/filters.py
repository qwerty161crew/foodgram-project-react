from django_filters import rest_framework as filter_

from recipe.models import Recipe


class RecipeFilter(filter_.FilterSet):
    tag = filter_.CharFilter(field_name='tag__title', lookup_expr='exact')

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'title', 'description',
                  'ingredients', 'tag', 'cooking_time', 'pub_date')
