from rest_framework import viewsets

from .pagination import CustomPagination
from .permissions import IsAuthOrReadOnly
from .serializers import RecipeSerializer


class RecipeViewser(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = IsAuthOrReadOnly
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)
