from django_filters import rest_framework as filters

from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    author = filters.CharFilter(field_name='author__id',
                                lookup_expr='icontains')
    tags = filters.CharFilter(field_name='tags__slug',
                              lookup_expr='icontains')
    is_favorited = filters.BooleanFilter(
        field_name='following_users',
        method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='shopping_users',
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['author', 'tags']

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(following_users=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shopping_users=self.request.user)
        return queryset
