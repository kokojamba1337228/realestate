from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save

class Property(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    location = models.CharField(max_length=100, null=True)
    size = models.FloatField(null=True)
    owner = models.ForeignKey('polls.CustomUser', on_delete=models.CASCADE, null=True, blank=True)
    pcreated_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.title
