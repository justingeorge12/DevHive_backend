
from rest_framework import serializers
from .models import *
from user.models import Users

class ProductSerializer(serializers.ModelSerializer):
    is_listed = serializers.BooleanField(default=True)  
    class Meta:
        model = Product
        fields = '__all__'


class UserCoinsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['coins']


class UserAddressSerializer(serializers.ModelSerializer):
    is_available = serializers.BooleanField(default=True)
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ['user']


class OrderSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    address = UserAddressSerializer()
    class Meta:
        model = Order
        fields =  ['id', 'product', 'user', 'coin', 'address', 'status', 'order_date', 'expected_date']
