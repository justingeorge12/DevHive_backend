from rest_framework import serializers
from .models import Users


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ["id", "username", "email", "password", "bio", "phone", "is_verified", "date_of_join", "coins", "location", "total_votes" ]
        extra_kwargs = {"password" : {"write_only":True}}

    def create(self, validated_data):
        user = Users.objects.create_user(**validated_data)
        return user 
    
class ListUsersSeralizer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'username','total_votes','profile', 'location']