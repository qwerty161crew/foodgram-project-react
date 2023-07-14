from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('recipes', views.RecipeViewset, basename='recipe')
router.register('users', views.ListUserViewset, basename='user')
router.register('set_password', views.ChangePasswordViewSet,
                basename='password_change')
router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart',
                views.AddRecipeInShoppingCart, basename='shopping_cart')
router.register('users/subscriptions',
                views.FollowSubscriptionsViewSet, basename='follow_list')
router.register(r'users/(?P<user_id>\d+)/subscriptions',
                views.FollowViewSet, basename='follow_create')
router.register(r'ingredients/(?P<ingredient_id>\d+)',
                views.IngridientsViewSet, basename='ingredient')

app_name = 'api'


urlpatterns = [path('', include((router.urls, 'api')))]
