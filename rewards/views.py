from django.shortcuts import render
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response

from datetime import timedelta
from django.utils.timezone import now

from .models import *
from .serializers import *
from user.models import Users
from user.serializers import UserSerializer
# Create your views here.



class ProductListView(ListAPIView):
    serializer_class = ProductSerializer

    
    def get_queryset(self):
        a =  Product.objects.filter(is_listed=True, quantity__gt=0).order_by('coins')

        print(a.explain(format='TEXT', analyze=True, verbose=True, timing=True, buffers=True))
        return a


    # def get_queryset(self):
    #     return Product.objects.filter(is_listed=True, quantity__gt=0).order_by('coins')
    


class ProductRetriveView(RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    def get(self, request, *args, **kwargs):
        # Get the product instance the user is trying to access
        product = self.get_object()

        if request.user.coins < product.coins:
            raise PermissionDenied("You do not have enough coins to access this product.")

        return super().get(request, *args, **kwargs)

    
class UserCoinDetail(RetrieveAPIView):
    queryset = Users.objects.all()
    serializer_class = UserCoinsSerializer

    def get_object(self):
        return self.request.user


class AddressViewModel(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = UserAddressSerializer 

    def get_queryset(self):
        user = self.request.user
        return Address.objects.filter(user = user)
    
    def perform_create(self, serializer):
        serializer.save(user = self.request.user)

    

class UserAddress(ListAPIView):
    queryset = Address.objects.all()
    serializer_class = UserAddressSerializer

    def get_queryset(self):
        print(self.request.user)
        return Address.objects.filter(user = self.request.user, is_available=True)
    




class CreateOrderView(APIView):

    def post(self, request, *args, **kwargs):
        user = request.user
        product_id = request.data.get('product_id')
        address_id = request.data.get('address_id')

        if not product_id or not address_id:
            raise ValidationError("Product ID and Address ID are required.")

        try:
            product = Product.objects.get(id=product_id, is_listed=True, quantity__gt=0)
        except Product.DoesNotExist:
            raise ValidationError("Product is either not listed or out of stock.")

        try:
            address = Address.objects.get(id=address_id, user=user)
        except Address.DoesNotExist:
            raise ValidationError("Invalid address ID.")

        if user.coins < product.coins:
            raise ValidationError("You do not have enough coins to place this order.")

        order = Order.objects.create(
            product=product,
            user=user,
            address=address,
            coin=product.coins,
            status="Ordered",
            expected_date=now().date() + timedelta(days=6),
            order_date=now().date(),
        )

        product.quantity -= 1
        product.save()

        user.coins -= product.coins
        user.save()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    



class UserOrdersView(ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-order_date')
    
