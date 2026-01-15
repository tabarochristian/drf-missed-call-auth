from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from rest_framework.settings import APISettings

USER_SETTINGS = getattr(settings, 'MISSEDCALL_AUTH', {})

DEFAULTS = {
    # List of allowed app signatures (e.g., SHA-256 hashes of your APK/IPA)
    'ALLOWED_APP_SIGNATURES': [],

    # Require app signature? If False, any non-empty string passes.
    'REQUIRE_SIGNATURE': True,

    # Session validity in seconds (default: 5 minutes)
    'VALIDITY_PERIOD': 300,

    # Optional: DRF Token model path (e.g., 'rest_framework.authtoken.Token')
    'TOKEN_MODEL': None,

    # Twilio credentials (can also be set via env vars)
    'TWILIO_ACCOUNT_SID': '',
    'TWILIO_AUTH_TOKEN': '',
}

# Apply settings
api_settings = APISettings(USER_SETTINGS, DEFAULTS)


# Optional: Validate critical settings at startup
def validate_settings():
    if api_settings.REQUIRE_SIGNATURE and not api_settings.ALLOWED_APP_SIGNATURES:
        raise ImproperlyConfigured(
            "MISSEDCALL_AUTH['REQUIRE_SIGNATURE'] is True, "
            "but 'ALLOWED_APP_SIGNATURES' is empty. "
            "Either provide allowed signatures or set REQUIRE_SIGNATURE=False."
        )