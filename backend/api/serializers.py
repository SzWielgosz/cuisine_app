from rest_framework import serializers
from .models import User, Profile, Category, Recipe, Ingredient, RecipeIngredient, Comment, Rating


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Profile
        fields = ['id', 'user', 'bio', 'website', 'profile_picture']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'description']


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    class Meta:
        model = Recipe
        fields = [
            'id', 'image', 'category', 'name', 'description', 'author',
            'created_at', 'updated_at', 'prep_time', 'prep_time_unit',
            'cook_time', 'cook_time_units', 'servings', 'ingredients'
        ]

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data


class RecipeIngredientSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer(read_only=True)
    ingredient = IngredientSerializer(read_only=True)
    class Meta:
        model = RecipeIngredient
        fields = ['id', 'recipe', 'ingredient', 'quantity', 'unit', 'note']


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'recipe', 'author', 'text', 'created_at']


class RatingSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    class Meta:
        model = Rating
        fields = ['id', 'recipe', 'author', 'score', 'created_at', 'updated_at']