from django.urls import path, include
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('products', views.ProductViewSet)
router.register('carts', views.CartViewSet, basename='carts')
router.register('customers', views.CustomerViewSet, basename='customers')
router.register('orders', views.OrderViewSet, basename='orders')

product_router = routers.NestedDefaultRouter(
    router, 'products', lookup='product')
product_router.register('reviews', views.ReviewViewSet,
                        basename='product-reviews')
product_router.register(
    'images', views.ProductImageViewSet, basename='product-images')
    
cart_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
cart_router.register('items', views.CartItemViewSet, basename='cart-items')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(cart_router.urls)),
    path('', include(product_router.urls)),
    path('collections/', views.CollectionList.as_view(), name='collection-list'),
    path('collections/<int:pk>/', views.collection_detail,
         name='collection-detail'),
]
