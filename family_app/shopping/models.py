from django.core.validators import MinValueValidator
from django.db import models
from decimal import Decimal

from django.db.models import ManyToManyField

from recipes.models import Unit

# Create your models here.

class MoveLackingItemOperationType(models.TextChoices):
    COPY = "copy"
    CUT = "cut"

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nazwa etykiety")
    
    class Meta:
        verbose_name = "Etykieta"
        verbose_name_plural = "Etykiety"
    
    def __str__(self):
        return self.name

class ShoppingListItem(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nazwa", unique=True)
    tags = ManyToManyField(Tag, blank=True, related_name="items", verbose_name="Etykiety")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Przedmiot zakupowy"
        verbose_name_plural = "Przedmioty zakupowe"
        
class LackingShoppingListItems(models.Model):
    shopping_list_item = models.OneToOneField(
        ShoppingListItem,
        on_delete=models.CASCADE,
        verbose_name="Przedmiot zakupowy"
    )
    quantity = models.DecimalField(max_digits=10, null=True, blank=True, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name="Ilość do kupienia")
    unit = models.CharField(max_length=10, choices=Unit, null=True, blank=True, verbose_name="Jednostka")
    extra_notes = models.CharField(max_length=1000, null=True, blank=True, verbose_name="Dodatkowe uwagi")
    is_checked = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Czas ostatniej aktualizacji")
    
    def __str__(self):
        return self.shopping_list_item.name
    
    class Meta:
        verbose_name = "Brakujący przedmiot zakupowy"
        verbose_name_plural = "Brakujące przedmioty zakupowe"
    
class ShoppingList(models.Model):
    title = models.CharField(max_length=200, verbose_name="Tytuł", unique=True)
    description = models.CharField(max_length=400, null=True, blank=True, verbose_name="Opis/uwagi")
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Lista zakupów"
        verbose_name_plural = "Listy zakupów"

class ShoppingItemsList(models.Model):
    shopping_list = models.ForeignKey(
        ShoppingList,
        on_delete=models.CASCADE
    )
    shopping_list_item = models.ForeignKey(
        ShoppingListItem,
        on_delete=models.CASCADE,
        verbose_name="Przedmiot zakupowy"
    )
    quantity = models.DecimalField(max_digits=10, null=True, blank=True, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name="Ilość")
    unit = models.CharField(max_length=10, choices=Unit, null=True, blank=True, verbose_name="Jednostka")
    extra_notes = models.CharField(max_length=1000, null=True, blank=True, verbose_name="Dodatkowe uwagi")
    is_checked = models.BooleanField(default=False)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.id)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["shopping_list", "shopping_list_item"], name="unique_item"
            )
        ]
        verbose_name = "Przedmiot zakupowy"
        verbose_name_plural = "Lista przedmiotów zakupowych"
        
class ListPushSubscription(models.Model):
    shopping_list = models.ForeignKey(
        ShoppingList,
        on_delete=models.CASCADE,
        related_name="push_subscriptions"
    )
    # Required Web Push fields provided by the browser
    endpoint = models.URLField(max_length=500)
    p256dh = models.CharField(max_length=200)
    auth = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensures one device cannot subscribe to the same list multiple times
        constraints = [
            models.UniqueConstraint(
                fields=["shopping_list", "endpoint"],
                name="unique_list_subscription"
            )
        ]

    def __str__(self):
        return f"Subscription for {self.shopping_list.title}"