from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('recipe', views.RecipeViewset, basename='recipe')
router.register('user', views.UserViewset, basename='user')
app_name = 'api'

urlpatterns = [path('', include((router.urls, 'api')))]
