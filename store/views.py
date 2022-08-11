from asyncio import mixins
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.decorators import action
from rest_framework import status
from .models import Cart, CartItem, Collection, Customer, Order, Product, Review
from .serializers import AddCartItemSerializer, CartItemSerializer, CartSerializer, CreateOrderSerializer, OrderSerializer, ProductSerializer, CollectionSerializer, ReviewSerializer, UpdateCartItemSerializer, CustomerSerializer
from .permissions import IsAdminOrReadOnly
# Create your views here.

# mixins.ListModelMixins, mixins.CreateModelMixins, GenericAPIView

# ModelViewSet : list, create, destroy, retrieve, update, GenericViewSet: (GenericAPIView, ViewSetMixin)


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        product = get_object_or_404(Product, pk=self.kwargs['pk'])
        if product.orderitem_set.count() > 0:
            return Response({'error': "Product cannot be deleted because it is associated with an order item."}, status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status.HTTP_204_NO_CONTENT)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}
# function based view


@api_view(['GET', 'PUT', 'DELETE'])
def collection_detail(request, pk):
    permission_classes = [IsAdminOrReadOnly]
    collection = get_object_or_404(Collection, pk=pk)
    if request.method == 'GET':
        serializer = CollectionSerializer(collection)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = CollectionSerializer(collection, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return(serializer.data)
    elif request.method == 'DELETE':
        if collection.product_set.count() > 0:
            return Response({'error': "Collection cannot be deleted."}, status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status.HTTP_204_NO_CONTENT)

# class-based view


class CollectionList(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        collections = Collection.objects.prefetch_related('product_set').all()
        serializer = CollectionSerializer(collections, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CollectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('product').all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer

        if self.request.method == 'PUT':
            return UpdateCartItemSerializer

        return CartItemSerializer

    def get_serializer_context(self):
        if self.request.method == 'POST':
            return {'cart_id': self.kwargs['cart_pk']}

        elif self.request.method == 'PUT':
            return {'cart_id': self.kwargs['cart_pk'], 'id': self.kwargs['pk']}


class CustomerViewSet (CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['GET', 'PUT'])
    def me(self, request):
        (customer, created) = Customer.objects.get_or_create(
            user_id=request.user.id)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class OrderViewSet (ModelViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data, context={
                                           'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def get_queryset(self):
        # print(self.kwargs)
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()

        (customer_id, created) = Customer.objects.only(
            'id').get_or_create(user_id=user.id)
        return Order.objects.filter(customer_id=customer_id)

    # serializer_class = OrderSerializer
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        return OrderSerializer
