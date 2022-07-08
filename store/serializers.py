from decimal import Decimal
from numpy import source
from rest_framework import serializers
from .models import Product, Collection


class CollectionSerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField(
        method_name="product_counts", read_only=True)

    def product_counts(self, collection: Collection):
        return collection.product_set.count()

    class Meta:
        model = Collection
        fields = ['id', 'title', 'product_count']


class ProductSerializer(serializers.ModelSerializer):
    # a custom field
    price_with_tax = serializers.SerializerMethodField(
        method_name='calculate_tax')

    price = serializers.DecimalField(
        max_digits=6, decimal_places=4, source='unit_price')

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)

    # collection = serializers.StringRelatedField()
    # collection_name = serializers.PrimaryKeyRelatedField(source='collection', write_only=True,
    #     queryset=Collection.objects.all())

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price_with_tax',
                  'price', 'collection' , 'inventory']