import re
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

# Standard E.164 validator (e.g., +12345678901)
phone_number_validator = RegexValidator(
    regex=r'^\+\d{10,15}$',
    message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
)