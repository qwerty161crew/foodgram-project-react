from django.shortcuts import render, get_object_or_404, redirect
from .paginations import get_page
from .models import Recipe


def index(request):
    recipes = Recipe.objects.all()
    page_obj = get_page(request.GET.get('page'), recipes)
    context = {
        'page_obj': page_obj,
    }
    return  # render(request, 'posts/index.html', context)
