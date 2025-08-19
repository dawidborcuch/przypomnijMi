from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    CATEGORY_CHOICES = [
        ('urodziny', 'Urodziny'),
        ('imieniny', 'Imieniny'),
        ('rocznice', 'Rocznice'),
        ('przeglad', 'Przegląd'),
        ('ubezpieczenie', 'Ubezpieczenie'),
        ('inne', 'Wpisz własną kategorię'),
    ]
    RECURRENCE_CHOICES = [
        ('none', 'Brak'),
        ('daily', 'Codziennie'),
        ('weekly', 'Co tydzień'),
        ('monthly', 'Co miesiąc'),
        ('yearly', 'Co rok'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    custom_category = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=255)
    is_recurring = models.BooleanField(default=False, verbose_name='Wydarzenie cykliczne')
    recurrence_type = models.CharField(max_length=10, choices=RECURRENCE_CHOICES, default='none')
    recurrence_end = models.DateField(blank=True, null=True, verbose_name='Powtarzaj do (włącznie)')
    icon = models.CharField(max_length=32, blank=True, default="fa-calendar-check", verbose_name="Ikona wydarzenia")

    def __str__(self):
        return f"{self.get_category_display()} - {self.date}: {self.description}"
