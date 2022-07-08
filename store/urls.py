from django.urls import path, include
from rest_framework.routers import DefaultRouter 
from . import views

router = DefaultRouter()
router.register('products',views.ProductViewSet)
urlpatterns = [
    path('', include(router.urls)),
    path('collections/',views.CollectionList.as_view(), name='collection-list'),
    path('collections/<int:pk>/',views.collection_detail, name='collection-detail'),
]