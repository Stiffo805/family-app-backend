from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from shopping.models import ShoppingList, ShoppingItemsList, ShoppingListItem

class ShoppingListsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingList
        fields = ['id', 'title', 'description']
        
class ShoppingItemsListSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(
        source='shopping_list_item.id',
        read_only=True
    )
    
    # We fetch the name of the product directly, replacing SlugRelatedField
    product_name = serializers.CharField(
        source='shopping_list_item.name',
        read_only=True
    )
    
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)
    
    class Meta:
        model = ShoppingItemsList
        fields = ['id', 'product_id', 'product_name', 'quantity', 'unit', 'unit_display', 'extra_notes', 'is_checked']

class ShoppingListSerializer(serializers.ModelSerializer):
    
    entries = ShoppingItemsListSerializer(source='shoppingitemslist_set', many=True, read_only=True)
    
    class Meta:
        model = ShoppingList
        fields = ['id', 'title', 'description', 'entries']