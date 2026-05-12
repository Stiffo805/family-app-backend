from django.contrib import admin

from item_register.models import ItemRegister, Item, Category, Room

# Register your models here.

class ItemRegisterAdmin(admin.ModelAdmin):
    readonly_fields = ['last_updated_at']

admin.site.register(ItemRegister, ItemRegisterAdmin)
admin.site.register(Item)
admin.site.register(Category)
admin.site.register(Room)