from decimal import Decimal
from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem, Product, Collection, Review, Customer


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
                  'price', 'collection', 'inventory']


class ReviewSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)

    class Meta:
        model = Review
        fields = ['id', 'date', 'title', 'description']


class SimpleProuctSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']


class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProuctSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, item: CartItem):
        return item.product.unit_price * item.quantity

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'total_price', 'quantity']


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No product with the given id')
        return value

    def save(self, **kwargs):
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        cart_id = self.context['cart_id']

        try:
            cart_item = CartItem.objects.get(
                product_id=product_id, cart_id=cart_id)
            cart_item.quantity = quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data)

        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class CartSerializer (serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart: Cart):
        total = 0
        for item in cart.items.all():
            total += item.product.unit_price * item.quantity
        return total

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']


class CustomerSerializer (serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = ['id', 'phone', 'birth_date', 'membership']


class OrderItemSerialzer (serializers.ModelSerializer):
    product = SimpleProuctSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price']


class OrderSerializer (serializers.ModelSerializer):
    items = OrderItemSerialzer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'payment_status', 'placed_at', 'items']
