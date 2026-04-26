from django.urls import path

from shopping.views import ShoppingListsView, ShoppingListView, ShoppingListItemView, SubscribeToListView, \
  UnsubscribeFromListView, ShoppingListItemsView, UnitsView, TagsView, LackingShoppingListItemsView, \
  LackingShoppingListItemView, move_lacking_items_to_list

urlpatterns = [
  path('lists/<int:list_id>/entries/<int:entry_id>/', ShoppingListItemView.as_view(), name='shopping-list-item-details'),
  path('lists/<int:list_id>/subscribe/', SubscribeToListView.as_view(), name='subscribe-list'),
  path('lists/<int:list_id>/unsubscribe/', UnsubscribeFromListView.as_view(), name='unsubscribe-list'),
  path('lists/<int:list_id>/', ShoppingListView.as_view(), name='shopping-list-details'),
  path('lists/', ShoppingListsView.as_view(), name='shopping-lists'),
  path('items/lacking/move/<int:target_list_id>/', move_lacking_items_to_list, name='move-lacking-items'),
  path('items/lacking/<int:item_id>/', LackingShoppingListItemView.as_view(), name='lacking-item'),
  path('items/lacking/', LackingShoppingListItemsView.as_view(), name='lacking-items'),
  path('items/', ShoppingListItemsView.as_view(), name='items'),
  path('units/', UnitsView.as_view(), name='units'),
  path('tags/', TagsView.as_view(), name='tags')
]