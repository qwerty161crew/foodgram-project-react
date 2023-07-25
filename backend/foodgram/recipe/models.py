from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, RegexValidator


class Ingredient(models.Model):
    """
    Ingredient Model
    """
    title = models.CharField(max_length=150, unique=True)
    measurement_unit = models.CharField(max_length=60)


class Tag(models.Model):
    title = models.CharField(max_length=50, unique=True)
    color = models.CharField(
        'Цветовой HEX-код',
        unique=True,
        max_length=7,
        validators=[
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Введенное значение не является цветом в формате HEX!'
            )
        ]
    )
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.title


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='author')
    title = models.CharField(max_length=50, unique=True)
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )
    text = models.CharField(max_length=1000)
    ingredients = models.ManyToManyField(
        Ingredient, related_name='ingredients')
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
        Recipe, related_name='is_favorited', on_delete=models.CASCADE)

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
    user = models.ForeignKey(User, related_name='user_cart',
                             on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe, related_name='is_in_shopping_cart', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.user.username} {self.recipe}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe'
            ),
        ]


class IngridientsRecipe(models.Model):
    ingridient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'{self.ingridient} {self.recipe}'
