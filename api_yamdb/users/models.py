from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from api_yamdb.settings import (NOT_MI_NAME,
                                RESERVED_NAME)


class MyUserManager(UserManager):
    """Сохраняем пользователя только с корректным email.
    Имя которое уже есть в базе использовать нельзя"""

    def create_user(self, username, email, password, **extra_fields):
        if not email:
            raise ValueError('Заполните поле email')
        if username == RESERVED_NAME:
            raise ValueError(NOT_MI_NAME)
        return super().create_user(
            username, email=email, password=password, **extra_fields)

    def create_superuser(
            self, username, email, password, role=None, **extra_fields):
        if role is None:
            role = 'admin'
        return super().create_superuser(
            username, email, password, **extra_fields, role=role)


class User(AbstractUser):
    """Формируем пользовательские роли"""
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLES = [
        (USER, USER),
        (MODERATOR, MODERATOR),
        (ADMIN, ADMIN)
    ]
    bio = models.TextField(blank=True)
    role = models.CharField(max_length=200, choices=ROLES, default=USER)
    username = models.CharField(max_length=150, unique=True, db_index=True)
    objects = MyUserManager()

    REQUIRED_FIELDS = ('email', 'password')

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_user(self):
        return self.role == self.USER
