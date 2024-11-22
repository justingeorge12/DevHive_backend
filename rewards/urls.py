from django.urls import path, include
from .views import * 
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'address', AddressViewModel, basename='address')


urlpatterns = [
    path('userproduct', ProductListView.as_view(), name='userproduct'),
    path('userproduct/<int:pk>', ProductRetriveView.as_view(), name='userproduct'),
    path('usercoins/', UserCoinDetail.as_view(), name='usercoins'),
    path('useraddress/',UserAddress.as_view(), name='useraddress' ),
    path('createorder/', CreateOrderView.as_view(), name='createorder'),
    path('userorders/',UserOrdersView.as_view(), name='userorders'),
    path('',include(router.urls)) 
]
