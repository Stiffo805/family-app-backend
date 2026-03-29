from rest_framework import serializers
from shopping.models import ListPushSubscription, ShoppingListItem

from shopping.models import ShoppingList, ShoppingItemsList

class ShoppingListsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingList
        fields = ['id', 'title', 'description']
        
class ShoppingItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingListItem
        fields = ['id', 'name']
        
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


# Serializer for the nested 'keys' object provided by the browser
class PushSubscriptionKeysSerializer(serializers.Serializer):
    p256dh = serializers.CharField(max_length=200)
    auth = serializers.CharField(max_length=200)


class ListPushSubscriptionSerializer(serializers.ModelSerializer):
    # Expect a nested dictionary named 'keys' in the request payload
    keys = PushSubscriptionKeysSerializer(write_only=True)
    
    class Meta:
        model = ListPushSubscription
        fields = ['endpoint', 'keys']
    
    def create(self, validated_data):
        # Extract the nested keys
        keys_data = validated_data.pop('keys')
        
        # We retrieve the specific shopping list from the serializer's context
        # (which we will pass in our view)
        shopping_list = self.context['shopping_list']
        
        # Create or update the subscription.
        # We use 'endpoint' as the unique identifier for the device's browser.
        subscription, created = ListPushSubscription.objects.update_or_create(
            shopping_list=shopping_list,
            endpoint=validated_data['endpoint'],
            defaults={
                'p256dh': keys_data['p256dh'],
                'auth': keys_data['auth']
            }
        )
        return subscription