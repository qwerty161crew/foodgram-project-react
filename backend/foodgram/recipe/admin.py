from django.contrib import admin
from recipe.models import (Recipe, Ingredient,
                           Tag,
                           FavoritesRecipe,
                           ShoppingList,
                           Follow,
                           IngredientsRecipe
                           )


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'text', 'cooking_time', 'author', 'image')
    search_fields = ('name',)
    list_filter = ('tags', 'pub_date')


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', )
    list_filter = ('color',)


class IngridientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', )
    list_filter = ('measurement_unit', )


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngridientAdmin)
admin.site.register(FavoritesRecipe)
admin.site.register(ShoppingList)
admin.site.register(Follow)
admin.site.register(IngredientsRecipe)
