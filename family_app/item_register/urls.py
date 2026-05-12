from django.urls import path

from item_register.views import ItemsRegisterView

urlpatterns = [
    path('register/', ItemsRegisterView.as_view(), name='items-register')
]