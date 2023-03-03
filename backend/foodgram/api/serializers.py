import base64

from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from django.forms import ValidationError
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from recipes.models import (FavoritedRecipe, Ingredient, Recipe, ShoppingCart,
                            Tag, TaggedRecipe, IngredientRecipe)
from users.models import Follow, User


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')  
            ext = format.split('/')[-1]  
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)
    

class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        if self.context.get('request'):
            user = self.context.get('request').user
            return Follow.objects.filter(user=user, author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            RegexValidator(
                regex=r'^[\w.@+-]{1,150}',
                message='Недопустимое имя пользователя'
            )
        ],
        required=True,
    )
    email = serializers.EmailField(
        validators=(
            UniqueValidator(queryset=User.objects.all()),
        )
    )
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'password', 'first_name', 'last_name')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')

    
class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        required=True
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = IngredientRecipeSerializer(many=True)
    author = CustomUserSerializer(default=serializers.CurrentUserDefault())
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')
        
    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return user in obj.following_users.all()
    
    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return user in obj.shopping_users.all()


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientRecipeSerializer(many=True)
    author = CustomUserSerializer(default=serializers.CurrentUserDefault())
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')
        
    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return user in obj.following_users.all()
    
    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return user in obj.shopping_users.all()

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            amount = ingredient.get('amount')
            ingredient = ingredient.get('id')
            IngredientRecipe.objects.create(
                ingredient=ingredient,
                recipe=recipe,
                amount=amount
            )
        return recipe
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.author = validated_data.get('author', instance.author)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.text = validated_data.get(
            'text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        tags = validated_data.get('tags', instance.tags)
        instance.tags.set(tags)
        if 'ingredients' in validated_data:
            ingredients_data = validated_data.get('ingredients')
            for ingredient in ingredients_data:
                amount = ingredient.get('amount')
                ingredient = ingredient.get('id')
                ir = IngredientRecipe.objects.filter(ingredient=ingredient,
                                                recipe=instance)
                instance.ingredients__amount = amount
                instance.save()
        else:
            instance.save()
        return instance 


class FavoritedRecipeSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    recipe = serializers.SlugRelatedField(
        slug_field="id",
        queryset=Recipe.objects.all()
    )

    class Meta:
        fields = '__all__'
        model = FavoritedRecipe
        validators = [UniqueTogetherValidator(
            queryset=FavoritedRecipe.objects.all(),
            fields=('user', 'recipe')
        )]


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    recipe = serializers.SlugRelatedField(
        slug_field="id",
        queryset=Recipe.objects.all(),
    )

    class Meta:
        fields = '__all__'
        model = ShoppingCart
        validators = [UniqueTogetherValidator(
            queryset=ShoppingCart.objects.all(),
            fields=('user', 'recipe')
        )]


class FollowingRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserFollowingListSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
    
    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = FollowingRecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data
    
    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return Follow.objects.filter(user=user, author=obj).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FollowingSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    author = serializers.SlugRelatedField(
        slug_field="id",
        queryset=User.objects.all(),
    )

    class Meta:
        fields = '__all__'
        model = Follow
        validators = [UniqueTogetherValidator(
            queryset=Follow.objects.all(),
            fields=('user', 'author')
        )]

    def validate(self, data):
        user = self.context['request'].user
        if user == data['author']:
            raise serializers.ValidationError(
                'Попытка подписки на себя'
            )
        return data
