from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.relations import PrimaryKeyRelatedField
from .models import User, Profile, Category, Recipe, Ingredient, RecipeIngredient, Comment, Rating
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate


class RegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        extra_kwargs = {'email': {'required': True}, 'username': {'required': True}}


    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError('Passwords must match.')
        validate_password(attrs['password1'])
        return attrs


    def create(self, validated_data):
        password = validated_data.pop('password1')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=password,
        )
        Profile.objects.create(user=user)
        return user


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


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer()
    class Meta:
        model = RecipeIngredient
        fields = ['id', 'ingredient', 'quantity', 'unit', 'note']


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    ingredient_id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    class Meta:
        model = RecipeIngredient
        fields = ['ingredient_id', 'quantity', 'unit', 'note']


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = PrimaryKeyRelatedField(queryset=Category.objects.all())
    ingredients = RecipeIngredientSerializer(many=True, read_only=True, source='recipeingredient_set')

    class Meta:
        model = Recipe
        fields = [
            'id', 'image', 'category', 'name', 'description', 'author',
            'created_at', 'updated_at', 'prep_time', 'prep_time_unit',
            'cook_time', 'cook_time_units', 'servings', 'ingredients'
        ]


class RecipeWriteSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = PrimaryKeyRelatedField(queryset=Category.objects.all())
    ingredients = RecipeIngredientWriteSerializer(many=True, write_only=True)

    class Meta:
        model = Recipe
        fields = ['id', 'image', 'category', 'name', 'description', 'author',
                  'created_at', 'updated_at', 'prep_time', 'prep_time_unit',
                  'cook_time', 'cook_time_units', 'servings', 'ingredients']

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)

        for item in ingredients_data:
            ingredient = Ingredient.objects.get(id=item['ingredient_id'])
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                quantity=item['quantity'],
                unit=item['unit'],
                note=item.get('note', '')
            )

        return recipe

    def validate(self, attrs):
        if len(attrs['ingredients']) < 2:
            raise serializers.ValidationError('You must provide at least 2 ingredients')
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


class RatingWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['score']

    def validate(self, attrs):
        user = self.context['request'].user
        request = self.context['request']

        if not user.is_authenticated:
            raise serializers.ValidationError('User is not authenticated')


        # recipe id from url
        recipe_id = self.context['view'].kwargs.get('pk')
        recipe = get_object_or_404(Recipe, id=recipe_id)


        if request.method == 'POST':
            if Rating.objects.filter(recipe=recipe).filter(author=user).exists():
                raise serializers.ValidationError('Rating already exists')

        if request.method in ['PUT', 'PATCH']:
            if Rating.objects.filter(recipe=recipe).filter(author=user).exists():
                raise serializers.ValidationError('Rating does not exist')


        attrs['recipe'] = recipe
        return attrs


    def create(self, validated_data):
        return Rating.objects.create(**validated_data)


    def update(self, instance, validated_data):
        instance.score = validated_data.get('score', instance.score)
        instance.save()
        return instance