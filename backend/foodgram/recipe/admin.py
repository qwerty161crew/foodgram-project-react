from django.contrib.auth.models import User
from django.contrib import admin

from recipe.models import (Recipe, Ingredient,
                           Tag,
                           FavoritesRecipe,
                           ShoppingList,
                           Follow,
                           IngredientsRecipe,
                           )


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', )
    list_filter = ('color',)


class IngredientAmountInline(admin.TabularInline):
    """Класс, позволяющий добавлять ингредиенты в рецепты."""

    model = IngredientsRecipe
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'text', 'cooking_time', 'author',
                    'image', 'favorinte_recipe_count')
    search_fields = ('name',)
    inlines = (IngredientAmountInline, )
    list_filter = ('tags', 'pub_date')

    @admin.display(description='favorite_count')
    def favorinte_recipe_count(self, obj):
        return FavoritesRecipe.objects.filter(recipe=obj.id).count()


class IngridientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', )
    list_filter = ('measurement_unit', )


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = search_fields = ('email', 'first_name', 'last_name')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngridientAdmin)
admin.site.register(FavoritesRecipe)
admin.site.register(ShoppingList)
admin.site.register(Follow)
admin.site.register(IngredientsRecipe)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
