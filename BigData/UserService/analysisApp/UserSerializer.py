from rest_framework import serializers
from .models import User,Co2,Eye,Emotion

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = [
            'user_id',
            'user_pwd',
            'name',
            'birth',
            'phone_number',
            'email',
            'gender',
            'serial_no1',
            ]
