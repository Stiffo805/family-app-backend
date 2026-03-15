from django.http import JsonResponse, Http404
from django.shortcuts import render
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from drf_spectacular.utils import extend_schema, inline_serializer

from shopping.models import ShoppingList, ShoppingItemsList
from shopping.serializers import ShoppingListsSerializer, ShoppingListSerializer


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