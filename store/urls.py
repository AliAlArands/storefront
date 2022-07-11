from django.urls import path, include
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('products', views.ProductViewSet)

product_router = routers.NestedDefaultRouter(
    router, 'products', lookup='product')
product_router.register('reviews', views.ReviewViewSet,
                        basename='product-reviews')
urlpatterns = [
    path('', include(router.urls)),
    path('', include(product_router.urls)),
    path('collections/', views.CollectionList.as_view(), name='collection-list'),
    path('collections/<int:pk>/', views.collection_detail,
         name='collection-detail'),
]
