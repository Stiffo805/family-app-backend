from django.db import models

# Create your models here.

class FamilyMember(models.Model):
    name = models.CharField(max_length=30, unique=True, verbose_name="Imię")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Członek rodziny"
        verbose_name_plural = "Członkowie rodziny"

class Activity(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nazwa")
    is_good = models.BooleanField(verbose_name="Czy pozytywna")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Aktywność"
        verbose_name_plural = "Aktywności"
    
class ActivitiesLog(models.Model):
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        verbose_name="Aktywność"
    )
    family_member = models.ForeignKey(
        FamilyMember,
        on_delete=models.CASCADE,
        verbose_name="Członek rodziny"
    )
    start_date = models.DateTimeField(verbose_name="Data rozpoczęcia aktywności")
    end_date = models.DateTimeField(verbose_name="Data zakończenia aktywności")
    
    def __str__(self):
        duration_str = str(self.end_date - self.start_date)
        return f"{self.family_member.name} - {self.activity.name} - {duration_str[:(len(duration_str) - 3)]}h"
    
    class Meta:
        verbose_name = "Rejestr aktywności"
        verbose_name_plural = "Rejestr aktywności"