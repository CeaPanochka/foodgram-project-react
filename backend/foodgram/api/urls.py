from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CreateDeleteFollowViewSet, CustomUserViewSet,
                    FavoriteRecipeViewSet, IngredientViewSet, ListFollowView,
                    RecipeViewSet, ShoppingCartViewSet, TagViewSet,
                    download_shopping_cart)

router = DefaultRouter()

router.register(r'users/subscriptions', ListFollowView,
                basename='subscriptions')
router.register(r'users/(?P<user_id>\d+)/subscribe', CreateDeleteFollowViewSet,
                basename='subscribe')
router.register(r'users', CustomUserViewSet)
router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite', FavoriteRecipeViewSet,
    basename='favorite_recipe'
)
router.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart', ShoppingCartViewSet,
    basename='shopping_cart'
)
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)


urlpatterns = [
    path('recipes/download_shopping_cart/',
         download_shopping_cart, name='download_chopping'),
    path('', include(router.urls)),
    path('', include('djoser.urls.base')),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/', include('djoser.urls.jwt')),
]
