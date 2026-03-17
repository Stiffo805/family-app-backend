from django.urls import path

from shopping.views import ShoppingListsView, ShoppingListView, ShoppingListItemView, SubscribeToListView, \
  UnsubscribeFromListView

urlpatterns = [
  path("lists/<int:list_id>/entries/<int:entry_id>/", ShoppingListItemView.as_view(), name="shopping-list-item-details"),
  path('lists/<int:list_id>/subscribe/', SubscribeToListView.as_view(), name='subscribe-list'),
  path('lists/<int:list_id>/unsubscribe/', UnsubscribeFromListView.as_view(), name='unsubscribe-list'),
  path("lists/<int:pk>/", ShoppingListView.as_view(), name="shopping-list-details"),
  path("lists/", ShoppingListsView.as_view(), name="shopping-lists"),
]