from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _



class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True, null=False)


    def __str__(self):
        return f"{self.id} {self.username} {self.email}"


    def save(self, *args, **kwargs):
   
        if self.password and not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2')):
            self.password = make_password(self.password)
        
        super().save(*args, **kwargs)


class Profile(models.Model):
    def user_profile_picture_path(instance, filename):
        return f'profile_pictures/{instance.user.username}/{filename}'
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to=user_profile_picture_path, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    


class Recipe(models.Model):
    class TimeUnits(models.TextChoices):
        MINUTES = 'minutes'
        HOURS = 'hours'

    image = models.ImageField(upload_to='recipe_images/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    prep_time = models.PositiveIntegerField()
    prep_time_unit = models.CharField(max_length=10, choices=TimeUnits.choices, blank=True)
    cook_time = models.PositiveIntegerField()
    cook_time_units = models.CharField(max_length=10, choices=TimeUnits.choices, blank=True)
    servings = models.PositiveIntegerField()

    def __str__(self):
        return 'Recipe for ' + self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return 'Ingredient ' + self.name


class RecipeIngredient(models.Model):
    class Unit(models.TextChoices):
        GRAMS = 'g', 'Grams'
        KILOGRAMS = 'kg', 'Kilograms'
        MILLILITERS = 'ml', 'Milliliters'
        LITERS = 'l', 'Liters'
        PIECES = 'pcs', 'Pieces'
        CUPS = 'cups', 'Cups'
        TABLESPOONS = 'tbsp', 'Tablespoons'
        TEASPOONS = 'tsp', 'Teaspoons'
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=10, choices=Unit.choices)
    note = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        unique_together = ('recipe', 'ingredient')


class Comment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.author.username + "'s " + 'comment'
    

class Rating(models.Model):
    class Score(models.IntegerChoices):
        VERY_BAD = 1, 'Very bad'
        BAD = 2, 'Bad'
        OKAY = 3, 'Okay'
        GOOD = 4, 'Good'
        EXCELLENT = 5, 'Excellent'
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='ratings')
    score = models.PositiveIntegerField(choices=Score.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.author.username + "'s rating for " + self.recipe
    