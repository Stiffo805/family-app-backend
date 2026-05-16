from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from item_register.models import ItemRegister, Room, Category
from item_register.serializers import ItemRegisterSerializer, RoomSerializer, CategorySerializer


# Create your views here.

class ItemsRegisterView(APIView):
    permission_classes = [IsAdminUser]
    
    @extend_schema(
        parameters=[OpenApiParameter(
            name='searchText',
            required=False,
            type=OpenApiTypes.STR,
            location='query'
        )]
    )
    def get(self, request: Request):
        search_text = request.query_params.get('searchText')
        if search_text:
            item_register_entries = ItemRegister.objects.filter(item__name__icontains=search_text)
        else:
            item_register_entries = ItemRegister.objects.all()
        return Response({"items": ItemRegisterSerializer(item_register_entries, many=True).data})
    
class RoomsView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request: Request):
        rooms = Room.objects.all()
        return Response({"items": RoomSerializer(rooms, many=True).data})
    
class CategoriesView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request: Request):
        categories = Category.objects.all()
        return Response({"items": CategorySerializer(categories, many=True).data})