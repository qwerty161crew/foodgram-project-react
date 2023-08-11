from . import views
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from foodgram.utils import FileDownloadListAPIView


router = DefaultRouter()
router.register('recipes', views.RecipeViewset, basename='recipe')
router.register('users/subscriptions',
                views.FollowSubscriptionsViewSet, basename='follow_list')
router.register(r'users/',
                views.FollowViewSet, basename='follow_create')
router.register('users', views.CustomUserViewSet, basename='user')
router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart',
                views.AddRecipeInShoppingCart, basename='shopping_cart')

router.register(r'ingredients',
                views.IngridientsViewSet, basename='ingredient')
router.register('tags', views.TagViewset, basename='tag')


app_name = 'api'


urlpatterns = [
    path('', include((router.urls, 'api'))),
    path('download/', FileDownloadListAPIView.as_view(), name='donwload'),
    path('users/', include('djoser.urls')),          # new
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
