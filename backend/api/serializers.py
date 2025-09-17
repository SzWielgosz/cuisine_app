from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField
from .models import User, Profile, Category, Recipe, Ingredient, RecipeIngredient, Comment, Rating


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        exclude = ('password',)


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


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)
    class Meta:
        model = RecipeIngredient
        fields = ['id', 'ingredient', 'quantity', 'unit', 'note']


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = PrimaryKeyRelatedField(queryset=Category.objects.all())
    ingredients = serializers.ListField(
        child=RecipeIngredientSerializer(),
        write_only=True,
    )
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

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)

        for item in ingredients:
            ingredient_id = item.get('id')
            quantity = item.get('quantity')
            unit = item.get('unit')
            note = item.get('note', '')

            ingredient = Ingredient.objects.get(id=ingredient_id)

            RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient, quantity=quantity, unit=unit, note=note)

        return recipe


    def validate(self, attrs):
        if len(attrs['ingredients']) < 2:
            raise serializers.ValidationError('You must provide at least 2 ingredients')
        if attrs['category'] not in Category.objects.all():
            raise serializers.ValidationError('You must provide a valid category')
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'recipe', 'author', 'text', 'created_at']


class RatingSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Rating
        fields = ['id', 'recipe', 'author', 'score', 'created_at', 'updated_at']