from django.contrib import admin
from recipe.models import Recipe, Ingredient, Tag, FavoritesRecipe, ShoppingList, Follow


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'cooking_time', 'author', 'image')
    search_fields = ('title',)
    list_filter = ('tag', 'ingredients', 'pub_date')


class TagAdmin(admin.ModelAdmin):
    list_display = ('title', 'color', 'slug')
    search_fields = ('title', )
    list_filter = ('color',)


class IngridientAdmin(admin.ModelAdmin):
    list_display = ('title', 'count', 'unit')
    search_fields = ('title', )
    list_filter = ('unit', )


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngridientAdmin)
admin.site.register(FavoritesRecipe)
admin.site.register(ShoppingList)
admin.site.register(Follow)
