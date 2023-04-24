from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


def true_years_validator(value):
    if value < 1900 or value > timezone.now().year:
        raise ValidationError(
            _('Указан неверный год: %(value)s,'
              'укажите год от 1900 по настоящее время!'),
            params={'value': value},
        )
