from django.http import JsonResponse, Http404
from django.views.generic.detail import BaseDetailView
from rest_framework.views import APIView

from . import models
from .models import Recipe, IngredientRecipe
from rest_framework.request import Request
from rest_framework.response import Response

from .serializers import RecipeSerializer, RecipeInfoSerializer


class RecipeDetail(APIView):
    def get_object(self, pk):
        try:
            return Recipe.objects.get(pk=pk)
        except Recipe.DoesNotExist:
            raise Http404
    
    def get(self, request: Request, pk):
        recipe = self.get_object(pk)
        serializer = RecipeSerializer(recipe)
        return JsonResponse(serializer.data)
    
class RecipesInfosList(APIView):
    def get(self, request):
        recipes_infos = Recipe.objects.all()
        serializer = RecipeInfoSerializer(recipes_infos, many=True)
        return JsonResponse({"recipes": serializer.data})