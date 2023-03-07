from django.core.validators import RegexValidator
from django.db import models

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=200
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=200
    )
    color = models.CharField(
        'Цвет в HEX',
        max_length=7,
        null=True,
        validators=[
            RegexValidator(
                '^#([a-fA-F0-9]{6})',
                message='Поле должно содержать HEX-код выбранного цвета.'
            )
        ]

    )
    slug = models.SlugField(
        'Уникальный слаг',
        max_length=200,
        unique=True,
        null=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(User, verbose_name='Автор',
                               on_delete=models.CASCADE,
                               related_name='recipes')
    name = models.CharField('Название', max_length=256)
    image = models.ImageField('Изображение',
                              upload_to='recipes/')
    text = models.TextField('Описание рецепта')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты',
        related_name='recipes')
    tags = models.ManyToManyField(Tag, through='TaggedRecipe',
                                  verbose_name='Теги', related_name='recipes')
    cooking_time = models.IntegerField(
        'Время готовки',
        help_text='Время приготовления в минутах')
    following_users = models.ManyToManyField(
        User, through='FavoritedRecipe',
        verbose_name='Избранное',
        related_name='recipes_is_favorite',
        blank=True)
    shopping_users = models.ManyToManyField(User, through='ShoppingCart',
                                            verbose_name='Корзина',
                                            related_name='recipes_in_cart',
                                            blank=True)
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, verbose_name='Ингредиент',
        related_name='recipe',
        on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe, verbose_name='Рецепт',
        related_name='ingredient_list',
        on_delete=models.CASCADE)
    amount = models.IntegerField('Количество')

    class Meta:
        verbose_name = 'Ингедиент и рецепт'
        verbose_name_plural = 'Ингредиенты и рецепты'


class TaggedRecipe(models.Model):
    tag = models.ForeignKey(Tag, verbose_name='Тег',
                            on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe, verbose_name='Рецепт',
        on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Тег и рецепт'
        verbose_name_plural = 'Теги и рецепты'


class FavoritedRecipe(models.Model):
    user = models.ForeignKey(User,
                             related_name='favorite_recipes',
                             on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe,
                               related_name='favorite_users',
                               on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingCart(models.Model):
    user = models.ForeignKey(User,
                             related_name='shopped_recipes',
                             on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe,
                               related_name='shopped_users',
                               on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Продуктовая корзина'
        verbose_name_plural = 'Продуктовые корзины'
