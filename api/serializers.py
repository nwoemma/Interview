from rest_framework import serializers
from accounts.models import User
from django.contrib.auth import get_user_model

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone', 'is_active','account_status', 'created_at', 'updated_at', )
    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User.profile.related.model
        fields = ('bio', 'profile_pic', 'created_at', 'updated_at', )