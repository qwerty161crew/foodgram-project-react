from django.db import models
from djangoHexadecimal.fields import HexadecimalField
from django.core.exceptions import ValidationError
from users.models import User


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
    count = models.PositiveIntegerField()
    unit = models.CharField(choices=UNIT_CHOICES, max_length=50)


class Tag(models.Model):
    title = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)


class Recipe(models.Model):
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


class Favourites_Recipe(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_author')
    recipes = models.ManyToManyField(Recipe)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='follower',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Кумир',
        related_name='following',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.author.username} {self.user.username}'

    class Meta:
        verbose_name = ('Подписка')
        verbose_name_plural = ('Подписки')
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            ),
        )
