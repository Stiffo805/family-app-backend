from django.views.generic.detail import DetailView

# Create your views here.

from . import models

class RecipeView(DetailView):
  model = models.Recipe
  