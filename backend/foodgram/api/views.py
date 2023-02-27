from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import generics, mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from recipes.models import (FavoritedRecipe, Ingredient, Recipe, ShoppingCart,
                            Tag)
from users.models import Follow, User

from .filters import RecipeFilter
from .pagination import MinLimitOffsetPagination
from .permissions import OwnerOrReadOnly, ReadOnly
from .serializers import (CustomUserCreateSerializer, CustomUserSerializer,
                          FavoritedRecipeSerializer, FollowingSerializer,
                          IngredientSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer,
                          UserFollowingListSerializer)


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer
    pagination_class = MinLimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        elif self.action == 'me':
            return CustomUserSerializer
        return super().get_serializer_class()
    
    def get_permissions(self):
        if self.action == 'retrieve':
            return (ReadOnly(),)
        return super().get_permissions() 
    

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = MinLimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (OwnerOrReadOnly,)

    def get_permissions(self):
        if self.action == 'retrieve':
            return (ReadOnly(),)
        return super().get_permissions() 


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class ListFollowView(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = UserFollowingListSerializer
    pagination_class = MinLimitOffsetPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        follow_obj = User.objects.filter(follower__user_id=self.request.user.id)
        return follow_obj


class PostDeleteViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    pass


class CreateDeleteFollowViewSet(PostDeleteViewSet):
    serializer_class = FollowingSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        author_id = self.kwargs.get('user_id')
        request.data['author'] = author_id
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def get_object(self):
        follow_obj = Follow.objects.filter(user=self.request.user)
        return follow_obj


class FavoriteRecipeViewSet(PostDeleteViewSet):
    serializer_class = FavoritedRecipeSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        recipe_id = self.kwargs.get('recipe_id')
        request.data['recipe'] = recipe_id
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_object(self):
        favorite_recipe_obj = FavoritedRecipe.objects.filter(user=self.request.user)
        return favorite_recipe_obj


class ShoppingCartViewSet(PostDeleteViewSet):
    serializer_class = ShoppingCartSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        recipe_id = self.kwargs.get('recipe_id')
        request.data['recipe'] = recipe_id
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_object(self):
        shopping_cart_recipe_obj = ShoppingCart.objects.filter(user=self.request.user)
        return shopping_cart_recipe_obj
    

class DownloadShoppingCartViewSet(generics.ListAPIView, viewsets.GenericViewSet):
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticated,)
    def get_queryset(self):
        user = self.request.user
        recipes = Recipe.objects.filter(shopping_users=user)
        shopping_cart = {}
        for recipe in recipes:
            for ingredient in recipe.ingredients.all():
                if ingredient.name not in shopping_cart:
                    shopping_cart[ingredient.name] = ingredient
                else:
                    shopping_cart[ingredient.name].amount += ingredient.amount
        lst = []
        for recipe in shopping_cart:
            lst.append(shopping_cart[recipe])
        return lst
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        response = HttpResponse(serializer.data, headers={
                                'Content-Type': 'text/plain',
                                'Content-Disposition': 'attachment; filename="ingredients.txt"',})
        return response
