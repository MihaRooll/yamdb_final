from django.db.models import Avg
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, status
from rest_framework.filters import SearchFilter

from api_yamdb.settings import DEFAULT_FROM_EMAIL
from users.models import User
from reviews.models import Category, Genre, Title, Review
from .serializers import (
    CategorySerializer, ForAdminSerializer,
    GenreSerializer, ForUserSerializer,
    TitleReadSerializer, UserSerializer,
    TitleWriteSerializer, TokenSerializer,
    ReviewSerializer, CommentSerializer
)
from .mixins import CreateListDestroyMixinSet
from .permissions import (
    IsAuthorOrAdministratorOrReadOnly,
    IsAdminOrReadOnly, IsAdmin
)
from .filters import TitleFilter


class SignUpAPI(APIView):
    """Регистрируем пользователя"""
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = ForUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        user, created = User.objects.get_or_create(username=username,
                                                   email=email)
        self.generating_confirmation_code_email(request, user)
        return Response({'email': email, 'username': username})

    def generating_confirmation_code_email(self, request, username):
        email = request.data.get('email')
        user = get_object_or_404(User, username=username)
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            'Confirmation code',
            f'{confirmation_code}',
            f'{DEFAULT_FROM_EMAIL}',
            [f'{email}'],
            fail_silently=False,
        )


class TokenAPI(APIView):
    """Выдача токена"""
    permission_classes = (AllowAny,)

    def post(self, request):
        """Если confirmation_code корректный, даем доступ"""

        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User,
            username=serializer.validated_data['username']
        )
        if default_token_generator.check_token(
            user,
            serializer.validated_data['confirmation_code']
        ):
            token = AccessToken.for_user(user)
            return Response(
                {'token': str(token)},
                status=status.HTTP_200_OK
            )
        return Response({
            'confirmation_code': 'Не верный код подтверждения'},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserAdmin(viewsets.ModelViewSet):
    """Работа с пользователями для администратора"""
    queryset = User.objects.all()
    serializer_class = ForAdminSerializer

    permission_classes = (IsAdmin,)
    filter_backends = (SearchFilter,)
    http_method_names = ['get', 'post', 'patch', 'delete']
    search_fields = ('username',)
    lookup_field = 'username'

    def get(self, request, *args, **kwargs):
        serializer = ForUserSerializer(request.user, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['get', 'patch'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        if request.method == 'GET':
            serializer = UserSerializer(self.request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        user = get_object_or_404(User, username=self.request.user)
        serializer = UserSerializer(
            user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=user.role)
        return Response(serializer.data)


class CategoryViewSet(CreateListDestroyMixinSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(CreateListDestroyMixinSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score'))
    serializer_class = TitleReadSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrAdministratorOrReadOnly,)

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        serializer.save(author=self.request.user, title=title)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        new_queryset = title.reviews.all()
        return new_queryset


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrAdministratorOrReadOnly,)

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        new_queryset = review.comments.all()
        return new_queryset
