from django.db import models
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

    def __str__(self):
        return self.title


class Tag(models.Model):
    title = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.title


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
    tag = models.ManyToManyField(Tag, related_name='tag')
    cooking_time = models.PositiveIntegerField()
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('-pub_date',)


class FavoritesRecipe(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user')
    recipe = models.ForeignKey(
        Recipe, related_name='recipes_fovorite', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = ('Избранное')
        verbose_name_plural = ('Избранные')
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipes'
            ),
        )


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


class ShoppingList(models.Model):
    user = models.ForeignKey(User, related_name='user_shoppin_list',
                             on_delete=models.CASCADE)
    recipes = models.ManyToManyField(Recipe, related_name='recipe')
