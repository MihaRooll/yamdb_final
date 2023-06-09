from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin,)
from rest_framework.viewsets import GenericViewSet


class CreateListDestroyMixinSet(CreateModelMixin, ListModelMixin,
                                DestroyModelMixin, GenericViewSet):
    pass


class CreateUserMixinSet(CreateModelMixin, ListModelMixin,
                         RetrieveModelMixin, DestroyModelMixin,
                         GenericViewSet):
    pass
