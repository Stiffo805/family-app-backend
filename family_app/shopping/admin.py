from django.contrib import admin

from shopping.models import ShoppingListItem, ShoppingList, ShoppingItemsList
from shopping.utils import notify_subscribers_about_update


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
    
    def save_related(self, request, form, formsets, change):
        """
        Overrides the default admin method to execute logic after all inline
        items have been successfully saved to the database.
        """
        # Call the parent method to ensure standard save operations finish first
        super().save_related(request, form, formsets, change)
        
        # At this point, the list and all its items are updated in the DB.
        # Fire a single notification to all subscribers.
        notify_subscribers_about_update(form.instance)

admin.site.register(ShoppingListItem)
admin.site.register(ShoppingList, ShoppingListAdmin)