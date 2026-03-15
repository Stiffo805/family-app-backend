from django.contrib import admin

from shopping.models import ShoppingListItem, ShoppingList, ShoppingItemsList

# Register your models here.

class ShoppingItemsListInline(admin.TabularInline):
    model = ShoppingItemsList
    extra = 1
    min_num = 1
    fields = ['shopping_list_item', 'quantity', 'unit', 'extra_notes']

class ShoppingListAdmin(admin.ModelAdmin):
    inlines = [ShoppingItemsListInline]
    readonly_fields = ('id',)
    fields = ['id', 'title', 'description']

admin.site.register(ShoppingListItem)
admin.site.register(ShoppingList, ShoppingListAdmin)