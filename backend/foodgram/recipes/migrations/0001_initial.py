# Generated by Django 3.2.17 on 2023-02-23 16:44

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FavoritedRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Избранный рецепт',
                'verbose_name_plural': 'Избранные рецепты',
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Ингредиент')),
                ('count', models.IntegerField(verbose_name='Количество')),
                ('measurement_unit', models.CharField(choices=[('шт', 'штук'), ('гр', 'грамм'), ('кг', 'килограмм')], max_length=200, verbose_name='Единица меры')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
            },
        ),
        migrations.CreateModel(
            name='IngredientRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.ingredient', verbose_name='Ингредиент')),
            ],
            options={
                'verbose_name': 'Ингедиент и рецепт',
                'verbose_name_plural': 'Ингредиенты и рецепты',
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Название')),
                ('image', models.ImageField(blank=True, upload_to='recipes/', verbose_name='Изображение')),
                ('text', models.TextField(verbose_name='Описание рецепта')),
                ('cooking_time', models.IntegerField(help_text='Время приготовления в минутах', verbose_name='Время готовки')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('following_users', models.ManyToManyField(blank=True, related_name='recipes_is_favorite', through='recipes.FavoritedRecipe', to=settings.AUTH_USER_MODEL, verbose_name='Избранное')),
                ('ingredients', models.ManyToManyField(related_name='recipes', through='recipes.IngredientRecipe', to='recipes.Ingredient', verbose_name='Ингредиенты')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Тег')),
                ('color', models.CharField(max_length=7, verbose_name='HEX-код')),
                ('slug', models.SlugField(max_length=200, unique=True, verbose_name='Ссылка на тег')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
            },
        ),
        migrations.CreateModel(
            name='TaggedRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe', verbose_name='Рецепт')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.tag', verbose_name='Тег')),
            ],
            options={
                'verbose_name': 'Тег и рецепт',
                'verbose_name_plural': 'Теги и рецепты',
            },
        ),
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopped_users', to='recipes.recipe')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopped_recipes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Продуктовая корзина',
                'verbose_name_plural': 'Продуктовые корзины',
            },
        ),
        migrations.AddField(
            model_name='recipe',
            name='shopping_users',
            field=models.ManyToManyField(blank=True, related_name='recipes_in_cart', through='recipes.ShoppingCart', to=settings.AUTH_USER_MODEL, verbose_name='Корзина'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(related_name='recipes', through='recipes.TaggedRecipe', to='recipes.Tag', verbose_name='Теги'),
        ),
        migrations.AddField(
            model_name='ingredientrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe', verbose_name='Рецепт'),
        ),
        migrations.AddField(
            model_name='favoritedrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_users', to='recipes.recipe'),
        ),
        migrations.AddField(
            model_name='favoritedrecipe',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_recipes', to=settings.AUTH_USER_MODEL),
        ),
    ]
