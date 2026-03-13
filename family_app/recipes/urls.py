from django.urls import path
from .views import RecipeDetail, RecipesInfosList

urlpatterns = [
  path("<int:pk>/", RecipeDetail.as_view(), name="recipe-detail"),
  path("", RecipesInfosList.as_view(), name="recipes")
]
