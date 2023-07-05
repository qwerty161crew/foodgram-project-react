from django.db import models
from django.contrib.auth.models import User
from djangoHexadecimal.fields import HexadecimalField
from django.core.exceptions import ValidationError


class Ingredient(models.Model):
    LITER = 'л.'
    MILLILITER = 'мл.'
    GRAM = 'гр.'
    UNIT_CHOICES = [
        (LITER,
         'литр'),
        (MILLILITER, 'милилитр'),
        (GRAM, 'грамм'),
    ]
    title = models.CharField(max_length=50)
    count = models.PositiveIntegerField(max_length=50)
    unit = models.CharField(choices=UNIT_CHOICES, max_length=50)


class Tag(models.Model):
    title = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)


class Ricipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='author')
    title = models.CharField(max_length=50)
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )
    description = models.CharField(max_length=1000)
    ingredients = models.ManyToManyField(Ingredient)
    tag = models.ManyToManyField(Tag)
    cooking_time = models.PositiveIntegerField()
