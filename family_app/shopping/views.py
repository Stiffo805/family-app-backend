from collections import defaultdict

from django.http import JsonResponse, Http404
from django.shortcuts import render
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from drf_spectacular.utils import extend_schema, inline_serializer

from shopping.models import ShoppingList, ShoppingItemsList, ListPushSubscription, ShoppingListItem
from shopping.serializers import ShoppingListsSerializer, ShoppingListSerializer, ListPushSubscriptionSerializer

from django.shortcuts import get_object_or_404

# Create your views here.

class ShoppingListsView(APIView):
    def get(self, request):
        shopping_lists = ShoppingList.objects.all()
        serializer = ShoppingListsSerializer(shopping_lists, many=True)
        return JsonResponse({"shopping_lists": serializer.data})
    
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

class ShoppingListView(APIView):
    def get_object(self, pk):
        return get_shopping_list(pk)
        
    def get(self, request: Request, pk):
        shopping_list = self.get_object(pk)
        serializer = ShoppingListSerializer(shopping_list)
        return JsonResponse(serializer.data)

class ShoppingListItemView(APIView):
    permission_classes = [IsAdminUser]
    
    def get_object(self, list_id: int, entry_id: int):
        return get_shopping_list_entry(list_id, entry_id)
    
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
        shopping_list_entry = self.get_object(list_id, entry_id)
        
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

class ShoppingListItemsView(APIView):
    def get(self, request: Request):
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
            
        return JsonResponse({"items": result})
        
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