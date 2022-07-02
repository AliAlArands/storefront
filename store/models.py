from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings

# Create your models here.

class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()


class Collection(models.Model):
    title = models.CharField(max_length=255)
    featuerd_product = models.ForeignKey(
        'Product', on_delete=models.SET_NULL, null=True, related_name='+')

    def __str__(self):
        return self.title

class Product (models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(null=True, blank=True)
    unit_price = models.DecimalField(validators=[MinValueValidator(1)],
                                     max_digits=6, decimal_places=2)
    inventory = models.IntegerField(validators=[MinValueValidator(1)])
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT)
    promotions = models.ManyToManyField(
        Promotion, related_name='products', blank=True)

    def __str__(self) -> str:
        return self.title