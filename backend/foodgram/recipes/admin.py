from django.contrib import admin

from .models import (FavoritedRecipe, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag, TaggedRecipe)


class TaggedRecipeInlane(admin.TabularInline):
    model = TaggedRecipe
    extra = 1


class IngredientRecipeInlane(admin.TabularInline):
    model = IngredientRecipe
    extra = 1


class TagAdmin(admin.ModelAdmin):
    inlines = [TaggedRecipeInlane]


class IngredientAdmin(admin.ModelAdmin):
    inlines = [IngredientRecipeInlane]


class RecipeAdmin(admin.ModelAdmin):
    inlines = [TaggedRecipeInlane, IngredientRecipeInlane]


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(FavoritedRecipe)
admin.site.register(ShoppingCart)
