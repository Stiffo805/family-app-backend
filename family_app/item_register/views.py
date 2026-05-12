from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from item_register.models import ItemRegister
from item_register.serializers import ItemRegisterSerializer


# Create your views here.

class ItemsRegisterView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request: Request):
        return Response({"items": ItemRegisterSerializer(ItemRegister.objects.all(), many=True).data})