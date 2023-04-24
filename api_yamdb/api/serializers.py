from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers, exceptions
from rest_framework.validators import UniqueValidator

from users.models import User
from users.validators import UnicodeUsernameValidator
from reviews.models import Category, Genre, Title, Review, Comment
from api_yamdb.settings import (NOT_MI_NAME,
                                NO_NAME,
                                RESERVED_NAME)
from .utils import validate_users


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=(UnicodeUsernameValidator(),)
    )

    class Meta:
        model = User
        fields = '__all__'


class ForUserSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=(UnicodeUsernameValidator(),)
    )
    first_name = serializers.CharField(required=False, max_length=150)
    last_name = serializers.CharField(required=False, max_length=150)
    bio = serializers.CharField(required=False)
    role = serializers.CharField(required=False, default=User.USER)

    def update(self, instance, validated_data):
        instance.email = validated_data.get("email", instance.email)
        instance.username = validated_data.get("username", instance.username)
        instance.first_name = validated_data.get(
            "first_name", instance.first_name)
        instance.last_name = validated_data.get(
            "last_name", instance.last_name)
        instance.bio = validated_data.get("bio", instance.bio)
        instance.role = validated_data.get("last_name", instance.role)
        return instance

    def validate(self, data):
        return validate_users(self, data)

    def create(self, validater_data):
        user = User.objects.create(
            username=self.validated_data('username',),
            email=self.validated_data('email',),
        )
        return user


class ForAdminSerializer(serializers.ModelSerializer):
    """Если имя уже есть в базе то выводим исключение.
    Сериализатор для Admin"""

    email = serializers.EmailField(validators=(UniqueValidator(
        queryset=User.objects.all()),),
        required=True, max_length=254)

    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=(UnicodeUsernameValidator(),)
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role')

    def validate(self, data):
        return validate_users(self, data)


class ConfirmationCodeSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()


class TokenSerializer(serializers.Serializer):
    """Генерируем токен"""
    username = serializers.CharField(max_length=200, required=True)
    confirmation_code = serializers.CharField(max_length=200, required=True)

    def validate_username(self, value):
        if value == RESERVED_NAME:
            raise serializers.ValidationError(NOT_MI_NAME)
        if not User.objects.filter(username=value).exists():
            raise exceptions.NotFound(NO_NAME)
        return value


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Genre


class TitleReadSerializer(serializers.ModelSerializer):
    """Отдельный сериализатор для произведений, только на чтение"""
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    """Отдельный сериализатор для записей"""
    category = serializers.SlugRelatedField(queryset=Category.objects.all(),
                                            slug_field='slug'
                                            )
    genre = serializers.SlugRelatedField(queryset=Genre.objects.all(),
                                         slug_field='slug',
                                         many=True
                                         )

    class Meta:
        fields = '__all__'
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if (
            request.method == 'POST'
            and Review.objects.filter(title=title, author=author).exists()
        ):
            raise ValidationError('Может существовать только один отзыв!')
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
