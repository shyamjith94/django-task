from django.db import models

# Create your models here.


class FileData(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    created_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=["name", "category", "price"]),
            models.Index(fields=["-created_at"]),  # descending index
        ]