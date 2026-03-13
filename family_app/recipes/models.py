from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from markdownx.models import MarkdownxField

# Create your models here.

class Unit(models.TextChoices):
  ITEM = "item", _("szt.")
  LITRE = "litre", _("l")
  MILLILITER = "milliliter", _("ml")
  KILOGRAM = "kilogram", _("kg")
  GRAM = "gram", _("g")
  SPOON = "spoon", _("łyżki")
  TEASPOON = "teaspoon", _("łyżeczki")
  SEED = "seed", _("ziarna")
  LEAF = "leaf", _("listki")
  
class Author(models.Model):
  name = models.CharField(max_length=40, verbose_name="Autor")
  
  def __str__(self):
    return self.name
  
  class Meta:
    verbose_name = "Autor"
    verbose_name_plural = "Autorzy przepisów"

class Ingredient(models.Model):
  name = models.CharField(max_length=100, verbose_name="Nazwa")

  def __str__(self):
    return self.name
  
  class Meta:
    verbose_name = "Składnik"
    verbose_name_plural = "Składniki"

class Equipment(models.Model):
  name = models.CharField(max_length=100, verbose_name="Nazwa")

  def __str__(self):
    return self.name
  
  class Meta:
    verbose_name = "Narzędzie"
    verbose_name_plural = "Narzędzia"

class Recipe(models.Model):
  title = models.CharField(max_length=100, verbose_name="Tytuł")
  author = models.ForeignKey(
    Author,
    on_delete=models.PROTECT,
    verbose_name="Autor przepisu",
    related_name="recipes"
  )
  preparation_time = models.DurationField(help_text="Format: HH:MM:SS", verbose_name="Czas przygotowania")
  required_equipment = models.ManyToManyField(Equipment, verbose_name="Wymagane narzędzia")
  description = MarkdownxField(max_length=4000, verbose_name="Opis")
  
  def __str__(self):
    return f"{self.title} - {self.author}"
  
  class Meta:
    constraints = [
      models.UniqueConstraint(
        fields=["title", "author"], name="unique_recipe"
      )
    ]
    verbose_name = "Przepis"
    verbose_name_plural = "Przepisy"
    
  

class IngredientRecipe(models.Model):
  recipe = models.ForeignKey(Recipe, on_delete=models.PROTECT, verbose_name="Przepis")
  ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT, verbose_name="Składnik")
  quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name="Ilość")
  unit = models.CharField(max_length=10, choices=Unit, verbose_name="Jednostka")
  
  class Meta:
    constraints = [
      models.UniqueConstraint(fields=['recipe', 'ingredient'], name='no-repeated-ingredient', violation_error_message='Ten składnik został już w innym miejscu dodany do tego przepisu')
    ]
  
  def __str__(self):
    return "Składnik"

