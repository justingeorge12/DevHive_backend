from rest_framework import serializers
from .models import Tag
from rest_framework.generics import RetrieveUpdateAPIView
from user.models import Users



class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

    def validate_name(self, value):
        if Tag.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("Tag with this name already exists.")
        return value


class UserRetriUpdate(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'username', 'email', 'date_joined', 'is_blocked']