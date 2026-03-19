from django.contrib import admin

from shopping.models import ShoppingListItem, ShoppingList, ShoppingItemsList, ListPushSubscription
from shopping.utils import notify_subscribers_about_update
import copy

# Register your models here.

class ShoppingItemsListInline(admin.TabularInline):
    model = ShoppingItemsList
    extra = 1
    min_num = 1
    fields = ['shopping_list_item', 'quantity', 'unit', 'extra_notes']
    
    def formfield_for_foreignkey(
        self, db_field, request, **kwargs
    ):
        if db_field.name == 'shopping_list_item':
            kwargs["queryset"] = db_field.related_model.objects.order_by('name')
            
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class ShoppingListAdmin(admin.ModelAdmin):
    inlines = [ShoppingItemsListInline]
    readonly_fields = ('id',)
    fields = ['id', 'title', 'description']
    
    def save_related(self, request, form, formsets, change):
        """
        Overrides the default admin method to execute logic after all inline
        items have been successfully saved to the database.
        """
        super().save_related(request, form, formsets, change)
        
        shopping_items_formset = formsets[0]
        
        # 1. Convert BaseManager/QuerySets to standard lists so we can append to them
        added_items = list(shopping_items_formset.new_objects)
        deleted_items = list(shopping_items_formset.deleted_objects)
        changed_items = []
        
        # 2. Iterate over changed objects.
        # changed_objects is a list of tuples: (instance, changed_fields_list)
        for obj, changed_fields in shopping_items_formset.changed_objects:
            
            # Check if our target field was modified during this save
            # ... inside the loop ...
            if 'shopping_list_item' in changed_fields:
                
                matched_form = next(f for f in shopping_items_formset.forms if f.instance == obj)
                old_obj = copy.copy(obj)
                
                # 1. Get the raw ID from the initial form data (e.g., 1)
                old_value_id = matched_form.initial.get('shopping_list_item')
                
                # 2. Append '_id' to the field name!
                # This tells Django ORM to set the foreign key integer directly,
                # bypassing the need for a full model instance.
                setattr(old_obj, 'shopping_list_item_id', old_value_id)
                
                deleted_items.append(old_obj)
                added_items.append(obj)
            
            else:
                # If the target field didn't change, treat it as a standard update
                changed_items.append(obj)
        
        # At this point, the list and all its items are updated in the DB.
        # Fire a single notification to all subscribers with our modified lists.
        notify_subscribers_about_update(form.instance, added_items, changed_items, deleted_items)

admin.site.register(ShoppingListItem)
admin.site.register(ShoppingList, ShoppingListAdmin)
admin.site.register(ListPushSubscription)