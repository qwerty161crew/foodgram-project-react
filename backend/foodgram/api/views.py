from rest_framework import viewsets

from .pagination import CustomPagination
from .permissions import IsAuthOrReadOnly, IsAdminOrReadOnly
from .serializers import RecipeSerializer, TagtSerializer
from .filters import RecipeFilter

from recipe.models import Recipe


class RecipeViewset(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthOrReadOnly, )
    filterset_class = RecipeFilter
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)


class TagViewset(viewsets.ModelViewSet):
    serializer_class = TagtSerializer
    permission_classes = IsAdminOrReadOnly
