from rest_framework import serializers
from . import models

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ingredient
        fields = ['id', 'name']
        
class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Equipment
        fields = ['id', 'name']
        
class IngredientRecipeSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ingredient.name')
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)
    
    class Meta:
        model = models.IngredientRecipe
        fields = ['name', 'quantity', 'unit', 'unit_display']
        
class RecipeSerializer(serializers.ModelSerializer):
    
    ingredients = IngredientRecipeSerializer(source='ingredientrecipe_set', many=True, read_only=True)
    
    required_equipment = EquipmentSerializer(many=True, read_only=True)
    
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )
    
    class Meta:
        model = models.Recipe
        fields = [
            'id', 'title', 'author', 'preparation_time',
            'description', 'ingredients', 'required_equipment'
        ]
        
class RecipeInfoSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )
    
    class Meta:
        model = models.Recipe
        fields = ['id', 'title', 'author', 'preparation_time']