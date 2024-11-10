from rest_framework import serializers
from .models import Follow


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
    

class FollowSerializer(serializers.ModelSerializer):
    follower_username = serializers.CharField(source='follower.username', read_only=True)
    following_username = serializers.CharField(source='following.username', read_only=True)

    class Meta:
        model = Follow
        fields = ['follower', 'follower_username', 'following', 'following_username']