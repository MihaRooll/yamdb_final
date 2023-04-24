from rest_framework import serializers

from users.models import User
from api_yamdb.settings import RESERVED_NAME


def validate_users(self, data):
    if_username = User.objects.filter(username=data.get('username'))
    if_email = User.objects.filter(email=data.get('email'))
    if User.objects.filter(username=data.get('username'),
                           email=data.get('email')).exists():
        return data
    if if_email:
        raise serializers.ValidationError(f'Почта {if_email}'
                                          f'уже использовалась')
    if if_username:
        raise serializers.ValidationError(f'Имя {if_username}'
                                          f'уже использовалось')
    if str(data.get('username')).lower() == RESERVED_NAME:
        raise serializers.ValidationError('Нельзя использовать имя me')
    return data
