from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (FavoritedRecipe, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag)
from rest_framework import generics, mixins, viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from users.models import Follow, User

from .filters import RecipeFilter
from .pagination import MinLimitOffsetPagination
from .permissions import OwnerOrReadOnly, ReadOnly
from .serializers import (CustomUserCreateSerializer, CustomUserSerializer,
                          FavoritedRecipeSerializer, FollowingSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          TagSerializer, UserFollowingListSerializer)


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
    serializer_class = RecipeCreateSerializer
    pagination_class = MinLimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (OwnerOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return (ReadOnly(),)
        elif self.action == 'create':
            return (IsAuthenticated(),)
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
        follow_obj = User.objects.filter(
            follower__user_id=self.request.user.id)
        return follow_obj


class PostDeleteViewSet(mixins.CreateModelMixin, generics.DestroyAPIView,
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
        author_id = self.kwargs.get('user_id')
        follow_obj = Follow.objects.filter(user=self.request.user,
                                           author=author_id)
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
        recipe_id = self.kwargs.get('recipe_id')
        favorite_recipe_obj = FavoritedRecipe.objects.filter(
            user=self.request.user,
            recipe=recipe_id)
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
        recipe_id = self.kwargs.get('recipe_id')
        shopping_cart_recipe_obj = ShoppingCart.objects.filter(
            user=self.request.user,
            recipe=recipe_id)
        return shopping_cart_recipe_obj


@api_view(['GET'])
def download_shopping_cart(request):
    print(request)
    user = request.user
    ingredients = (IngredientRecipe.objects
                   .filter(recipe__shopping_users=user)
                   .values('ingredient')
                   .annotate(sum_amount=Sum('amount'))
                   .values_list('ingredient__name',
                                'ingredient__measurement_unit',
                                'sum_amount'))
    file_list = []

    [
        file_list.append(
            '{} {} - {}'
            .format(*ingredient)) for ingredient in ingredients
    ]

    file = HttpResponse(
        'Список покупок: \n' + '\n'.join(file_list),
        headers={'Content-Type': 'text/plain',
                 'Content-Disposition': ('attachment;'
                                         'filename="ingredients.txt"')}
    )

    return file
