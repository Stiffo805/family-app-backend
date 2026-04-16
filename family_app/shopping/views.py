from collections import defaultdict
from django.http import JsonResponse, Http404
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from drf_spectacular.utils import extend_schema, inline_serializer

from recipes.models import Unit
from shopping.models import ShoppingList, ShoppingItemsList, ListPushSubscription, ShoppingListItem, Tag
from shopping.serializers import ShoppingListsSerializer, ShoppingListSerializer, ListPushSubscriptionSerializer, \
    ShoppingItemSerializer, TagSerializer

from django.shortcuts import get_object_or_404

# Create your views here.

def get_shopping_list(pk):
    try:
        return ShoppingList.objects.get(pk=pk)
    except ShoppingList.DoesNotExist:
        raise Http404


def get_shopping_list_entry(list_id: int, entry_id: int):
    try:
        return ShoppingItemsList.objects.get(
            shopping_list_id=list_id,
            id=entry_id
        )
    except ShoppingItemsList.DoesNotExist:
        raise Http404


def get_shopping_list_item(item_id: int):
    try:
        return ShoppingListItem.objects.get(
            id=item_id
        )
    except ShoppingListItem.DoesNotExist:
        raise Http404
    
def is_shopping_list_item_in_list(list_id: int, item_id: int):
    item = get_shopping_list_item(item_id)
    shopping_list = get_shopping_list(list_id)
    try:
        ShoppingItemsList.objects.get(
            shopping_list=shopping_list,
            shopping_list_item=item
        )
        return True
    except ShoppingItemsList.DoesNotExist:
        return False

class ShoppingListsView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        shopping_lists = ShoppingList.objects.all()
        serializer = ShoppingListsSerializer(shopping_lists, many=True)
        return JsonResponse({"shopping_lists": serializer.data})
    
class ShoppingListView(APIView):
    permission_classes = [IsAdminUser]
    
    def get_object(self, list_id):
        return get_shopping_list(list_id)
        
    def get(self, request: Request, list_id: int):
        shopping_list = self.get_object(list_id)
        serializer = ShoppingListSerializer(shopping_list)
        return JsonResponse(serializer.data)
    
    @extend_schema(
        # This tells Swagger what the request body should look like
        request=inline_serializer(
            name='CreateItem',
            fields={
                'item_id': serializers.IntegerField(),
                'quantity': serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True),
                'unit': serializers.CharField(allow_null=True, allow_blank=True),
                'extra_notes': serializers.CharField(max_length=1000, allow_null=True, allow_blank=True)
            }
        )
    )
    def post(self, request: Request, list_id: int):
        shopping_list = get_shopping_list(list_id)
        shopping_item = get_shopping_list_item(request.data.get('item_id'))
        
        if is_shopping_list_item_in_list(list_id, request.data.get('item_id')):
            return Response(
                status=status.HTTP_409_CONFLICT,
                data={"error": "This shopping item already exists in the list"}
            )
        
        new_shopping_list_item = ShoppingItemsList(
            shopping_list=shopping_list,
            shopping_list_item=shopping_item,
            quantity=request.data.get('quantity'),
            unit=request.data.get('unit'),
            extra_notes=request.data.get('extra_notes')
        )
        new_shopping_list_item.save()
        return Response(
            status=status.HTTP_200_OK
        )


class ShoppingListItemView(APIView):
    permission_classes = [IsAdminUser]
    
    def get_entry(self, list_id: int, entry_id: int):
        return get_shopping_list_entry(list_id, entry_id)
    
    def get_object(self, item_id: int):
        return get_shopping_list_item(item_id)
        
    @extend_schema(
        # This tells Swagger what the request body should look like
        request=inline_serializer(
            name='ToggleItemCheck',
            fields={
                'is_checked': serializers.BooleanField()
            }
        ),
        # Optional: Tells Swagger what the response will look like
        responses={200: inline_serializer(
            name='ToggleItemResponse',
            fields={
                'status': serializers.CharField(),
                'is_checked': serializers.BooleanField()
            }
        )}
    )
    def patch(self, request: Request, list_id: int, entry_id: int):
        shopping_list_entry = self.get_entry(list_id, entry_id)
        
        # In DRF, parsed JSON payload is accessed via request.data
        is_checked_value = request.data.get('is_checked')
        
        if is_checked_value is not None:
            shopping_list_entry.is_checked = is_checked_value
            shopping_list_entry.save()
            
            return Response({
                'status': 'success',
                'is_checked': shopping_list_entry.is_checked
            }, status=status.HTTP_200_OK)
        
        return Response(
            {'error': 'The is_checked field is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @extend_schema(
        # This tells Swagger what the request body should look like
        request=inline_serializer(
            name='EditItem',
            fields={
                'quantity': serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True),
                'unit': serializers.CharField(allow_null=True, allow_blank=True),
                'extra_notes': serializers.CharField(max_length=1000, allow_null=True, allow_blank=True)
            }
        )
    )
    def put(self, request: Request, list_id: int, entry_id: int):
        shopping_list_entry = self.get_entry(list_id, entry_id)
        quantity = request.data.get('quantity')
        unit = request.data.get('unit')
        extra_notes = request.data.get('extra_notes')
        
        shopping_list_entry.quantity = quantity
        shopping_list_entry.unit = unit
        shopping_list_entry.extra_notes = extra_notes
        
        shopping_list_entry.save()
        
        return Response(
            status=status.HTTP_200_OK
        )
    def delete(self, request: Request, list_id: int, entry_id: int):
        shopping_list_entry = self.get_entry(list_id, entry_id)
        shopping_list_entry.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
    

class ShoppingListItemsView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request: Request):
        # --- Anywhere unchecked items ---
        shopping_items_lists = ShoppingItemsList.objects.filter(is_checked=False)
        item_to_shopping_lists_names = defaultdict(list)
        
        for shopping_item in shopping_items_lists:
            ingredient_id = shopping_item.shopping_list_item.id
            ingredient_name = shopping_item.shopping_list_item.name
            shopping_list_title = shopping_item.shopping_list.title
            item_to_shopping_lists_names[(ingredient_id, ingredient_name)].append(shopping_list_title)
        
        result = []
        
        for (ingredient_id, ingredient_name), shopping_lists_names in item_to_shopping_lists_names.items():
            result.append({
                "ingredient_id": ingredient_id,
                "ingredient_name": ingredient_name,
                "shopping_lists_names": shopping_lists_names
            })
            
        # --- All items ---
        all_items = ShoppingListItem.objects.all()
            
        return JsonResponse({
            "anywhere_unchecked_items": result,
            "all_items": ShoppingItemSerializer(all_items, many=True).data
        })
        
class UnitsView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request: Request):
        units_data = [
            {"value": key, "label": label}
            for key, label in Unit.choices
        ]
        return JsonResponse({"units": units_data})

class TagsView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request: Request):
        all_tags = Tag.objects.all()
        res = TagSerializer(all_tags, many=True).data
        return JsonResponse({"items": res})

class SubscribeToListView(APIView):
    # Enforce token authentication, as requested previously
    permission_classes = [IsAdminUser]
    
    @extend_schema(
        request=ListPushSubscriptionSerializer,
        responses={201: {"type": "object", "properties": {"status": {"type": "string"}}}}
    )
    def post(self, request, list_id: int):
        # Ensure the target shopping list exists, otherwise return 404
        shopping_list = get_object_or_404(ShoppingList, id=list_id)
        
        # Initialize the serializer, passing the list instance via context
        serializer = ListPushSubscriptionSerializer(
            data=request.data,
            context={'shopping_list': shopping_list}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": "Successfully subscribed to list notifications"},
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UnsubscribeFromListView(APIView):
    permission_classes = [IsAdminUser]
    
    @extend_schema(
        request=inline_serializer(
            name='UnsubscribePayload',
            fields={'endpoint': serializers.URLField()}
        ),
        responses={200: {"type": "object", "properties": {"status": {"type": "string"}}}}
    )
    def post(self, request, list_id: int):
        # The browser's unique endpoint URL
        endpoint = request.data.get('endpoint')
        
        if not endpoint:
            return Response(
                {"error": "Endpoint is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Delete the specific subscription record for this device and this list
        deleted_count, _ = ListPushSubscription.objects.filter(
            shopping_list_id=list_id,
            endpoint=endpoint
        ).delete()
        
        if deleted_count > 0:
            return Response(
                {"status": "Successfully unsubscribed from list"},
                status=status.HTTP_200_OK
            )
        
        # If the record didn't exist, we still return 200 OK
        # because the end goal (user not being subscribed) is met.
        return Response(
            {"status": "Subscription did not exist"},
            status=status.HTTP_200_OK
        )