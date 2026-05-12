from django.core.validators import MinValueValidator
from django.db import models
from decimal import Decimal

from recipes.models import Unit

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nazwa")
    
    class Meta:
        verbose_name = "Kategoria przedmiotu"
        verbose_name_plural = "Kategorie przedmiotów"
        
    def __str__(self):
        return self.name

class Item(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nazwa")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Kategoria"
    )
    
    class Meta:
        verbose_name = "Przedmiot"
        verbose_name_plural = "Przedmioty"
        
    def __str__(self):
        return self.name
    
class Room(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nazwa")
    
    class Meta:
        verbose_name = "Pokój"
        verbose_name_plural = "Pokoje"
        
    def __str__(self):
        return self.name
    
class ItemRegister(models.Model):
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        verbose_name="Przedmiot"
    )
    quantity = models.DecimalField(max_digits=10, null=True, blank=True, decimal_places=2,
                                   validators=[MinValueValidator(Decimal('0.01'))], verbose_name="Ilość")
    unit = models.CharField(max_length=10, choices=Unit, null=True, blank=True, verbose_name="Jednostka")
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Pokój"
    )
    place_description = models.CharField(max_length=1000, null=True, blank=True, verbose_name="Opis miejsca")
    last_updated_at = models.DateTimeField(auto_now=True, verbose_name="Data ostatniej aktualizacji")
    
    class Meta:
        verbose_name = "Rejestr przedmiotu"
        verbose_name_plural = "Rejestr przedmiotów"
        
    def __str__(self):
        return self.item.name