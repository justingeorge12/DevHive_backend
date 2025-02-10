from rest_framework import serializers
from .models import Users
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import ValidationError


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ["id", "username", "email", "password", "bio", "skill", "phone", "is_verified", "is_blocked", "date_of_join", "coins", "location", "total_votes", "profile", "first_name" ]
        extra_kwargs = {"password" : {"write_only":True},  "username": {"required": False}}

    def create(self, validated_data):

        username = validated_data.get('first_name')
        c = 1

        while Users.objects.filter(username=username).exists():
            username = f"{validated_data.get('first_name')}{c}"
            c += 1

        validated_data['username'] = username

        user = Users.objects.create_user(**validated_data)
        return user 
    



    
class ListUsersSeralizer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    class Meta:
        model = Users
        fields = ['id', 'username','total_votes','profile', 'location']
    
    def get_profile(self, obj):
        request = self.context.get('request')
        if obj.profile and obj.profile:
            return request.build_absolute_uri(obj.profile.url)
        return None



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        if user.is_superuser:
            role = 'admin'
        else:
            role = 'user'


        token['role'] = role  
        token['is_verified'] = user.is_verified
        token['user_id'] = user.id 
        
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        if self.user.is_blocked:
            raise ValidationError(
                {"detail": "This account is blocked and cannot log in.", "status": "blocked_account"}
            )
        
        if self.user.is_superuser:
            role = 'admin'
        else:
            role = 'user'

        data['role'] = role  
        data['is_verified'] = self.user.is_verified
        data['user_id'] = self.user.id
        return data

