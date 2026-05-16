from django.urls import path

from item_register.views import ItemsRegisterView, RoomsView, CategoriesView

urlpatterns = [
    path('register/', ItemsRegisterView.as_view(), name='items-register'),
    path('rooms/', RoomsView.as_view(), name='rooms'),
    path('categories/', CategoriesView.as_view(), name='categories')
]