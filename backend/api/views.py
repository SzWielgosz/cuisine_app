import datetime
from datetime import timedelta, timezone

from django.db import transaction
from django.utils.http import urlsafe_base64_decode
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from rest_framework import generics
from .permissions import IsAuthorOrReadOnly, IsAdminOrReadOnly
from .services import send_activation_email
from .tokens import account_activation_token
from django.conf import settings


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
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        return Rating.objects.filter(recipe=recipe)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RatingWriteSerializer
        return RatingSerializer

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        serializer.save(author=self.request.user, recipe=recipe)


class ReadUpdateDeleteRatingView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rating.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RatingSerializer
        return RatingWriteSerializer


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


class RegisterApiView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        user = serializer.save()
        send_activation_email(user)


    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data = {
            "message": "User registered successfully. Check your email for activation link!"
        }
        return response



class ActivateUserView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid uidb64 or token'}, status=status.HTTP_404_NOT_FOUND)

        if account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'message': 'Account activated successfully.'})
        else:
            return Response({'message': 'Activation link is invalid.'})


class SendActivationEmailView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SendActivationEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        send_activation_email(user)
        return Response({'message': 'Activation email sent.'})