from rest_framework import serializers

from item_register.models import ItemRegister, Item, Category, Room


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ItemSerializer(serializers.ModelSerializer):
    
    category = CategorySerializer()
    
    class Meta:
        model = Item
        fields = ['id', 'name', 'category']

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name']

class ItemRegisterSerializer(serializers.ModelSerializer):
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)
    
    item = ItemSerializer()
    room = RoomSerializer()
    
    class Meta:
        model = ItemRegister
        fields = ['id', 'item', 'quantity', 'unit', 'unit_display', 'room', 'place_description', 'last_updated_at']