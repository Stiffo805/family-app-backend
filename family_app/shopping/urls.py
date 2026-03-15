from django.urls import path

from shopping.views import ShoppingListsView, ShoppingListView, ShoppingListItemView

urlpatterns = [
  path("lists/<int:list_id>/entries/<int:entry_id>/", ShoppingListItemView.as_view(), name="shopping-list-item-details"),
  path("lists/<int:pk>/", ShoppingListView.as_view(), name="shopping-list-details"),
  path("lists/", ShoppingListsView.as_view(), name="shopping-lists"),
]