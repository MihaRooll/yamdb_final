from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import UserAdmin, TokenAPI, SignUpAPI
from .views import (
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
    ReviewViewSet,
    CommentViewSet
)


router_v1 = DefaultRouter()

router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register('users', UserAdmin, basename='users')
router_v1.register('users/me/', UserAdmin, basename='users')
router_v1.register(r'titles/(?P<title_id>\d+)/reviews',
                   ReviewViewSet, basename='reviews')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments')

urlpatterns = [
    path('v1/auth/signup/', SignUpAPI.as_view(), name='signup'),
    path('v1/auth/token/', TokenAPI.as_view(), name='token'),
    path('v1/', include(router_v1.urls)),
]
