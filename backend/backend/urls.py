"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from api.views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register', RegisterApiView.as_view()),
    path('api/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/recipes/', RecipeListCreateView.as_view()),
    path('api/recipes/<int:pk>', RecipeDetailView.as_view()),
    path('api/recipes/<int:pk>/comments', ListCreateCommentView.as_view()),
    path('api/recipes/<int:pk>/ratings', ListCreateRatingView.as_view()),
    path('api/recipes/<int:pk>/ingredients', RecipeIngredientAPIView.as_view()),

    path('api/ingredients', IngredientListView.as_view()),

    path('api/categories', CategoryListView.as_view()),
    path('api/categories/<int:pk>', CategoryDetailView.as_view()),

    path('api/comments/<int:pk>', CommentDetailView.as_view()),

    path('api/ratings/<int:pk>', ReadUpdateDeleteRatingView.as_view()),
]
