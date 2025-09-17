from rest_framework import permissions
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from rest_framework import generics
from .permissions import IsAuthorOrReadOnly, IsAdminOrReadOnly


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class RecipeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]


class ListCreateCommentView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = CommentSerializer

    def get_queryset(self):
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        return Comment.objects.filter(recipe=recipe)

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        serializer.save(author=self.request.user, recipe=recipe)


class RecipeListCreateView(generics.ListCreateAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class IngredientListView(generics.ListAPIView):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrReadOnly]


class ListCreateRatingView(generics.ListCreateAPIView):
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        return Rating.objects.filter(recipe=recipe)

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        serializer.save(author=self.request.user, recipe=recipe)


class RatingView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class RecipeIngredientAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        recipe_ingredients = RecipeIngredient.objects.filter(recipe=recipe)
        serializer = RecipeIngredientSerializer(recipe_ingredients, many=True)
        return Response(serializer.data)