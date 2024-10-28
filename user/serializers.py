from rest_framework import serializers
from .models import Users
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ["id", "username", "email", "password", "bio", "skill", "phone", "is_verified", "date_of_join", "coins", "location", "total_votes", "profile", "first_name" ]
        extra_kwargs = {"password" : {"write_only":True}}

    def create(self, validated_data):
        user = Users.objects.create_user(**validated_data)
        return user 
    
class ListUsersSeralizer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'username','total_votes','profile', 'location']



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        if user.is_superuser:
            role = 'admin'
        else:
            role = 'user'

        print(user)

        token['role'] = role  
        token['is_verified'] = user.is_verified
        
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        
        if self.user.is_superuser:
            role = 'admin'
        else:
            role = 'user'

        data['role'] = role  
        data['is_verified'] = self.user.is_verified
        
        return data


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required = True)
    new_password = serializers.CharField(required = True)
    print(current_password)
    print(new_password)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value