from . import views
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('recipes', views.RecipeViewset, basename='recipe')

router.register('users', views.CustomUserViewSet, basename='user')

router.register(r'ingredients',
                views.IngridientsViewSet, basename='ingredient')
router.register('tags', views.TagViewset, basename='tag')


app_name = 'api'


urlpatterns = [
    path('', include((router.urls, 'api'))),
    path('users/', include('djoser.urls')),          # new
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
