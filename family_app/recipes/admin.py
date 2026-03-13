from django.contrib import admin
from . import models
from markdownx.widgets import AdminMarkdownxWidget

# Register your models here.

class IngredientRecipeInline(admin.TabularInline):
  model = models.IngredientRecipe
  verbose_name = "Składnik przepisu"
  verbose_name_plural = "Składniki przepisu"
  extra = 1
  min_num = 1
  fields = ['ingredient', 'quantity', 'unit']

class RecipeAdmin(admin.ModelAdmin):
  inlines = [IngredientRecipeInline]
  readonly_fields = ("id",)
  fields = ('id', 'title', 'author', 'preparation_time', 'description', 'required_equipment')
  
  def formfield_for_manytomany(self, db_field, request, **kwargs):
    if db_field.name == "ingredients":
      kwargs["queryset"] = models.Ingredient.objects
    if db_field.name == "required_equipment":
      kwargs["queryset"] = models.Equipment.objects
    if db_field.name == "description":
      kwargs["widget"] = AdminMarkdownxWidget
    return super().formfield_for_manytomany(db_field, request, **kwargs)
  
admin.site.register(models.Recipe, RecipeAdmin)
admin.site.register(models.Ingredient)
admin.site.register(models.Equipment)
admin.site.register(models.Author)