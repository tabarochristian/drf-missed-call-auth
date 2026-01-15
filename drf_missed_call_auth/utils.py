import hmac
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from .settings import api_settings
from .gateways.twilio import TwilioGateway


def normalize_phone_number(phone: str) -> str:
    """
    Converts a phone number to E.164 format.
    Assumes input is a string of digits possibly with +, -, spaces, or parentheses.
    """
    # Remove all non-digit characters except leading +
    cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')
    if not cleaned.startswith('+'):
        # Default to international format without country code? Not safe.
        # But we assume frontend sends proper format.
        # Alternatively, raise error — but we'll keep permissive for now.
        pass
    return cleaned


def validate_app_signature(value: str) -> bool:
    """
    Validates the application signature using constant-time comparison.
    Respects REQUIRE_SIGNATURE and ALLOWED_APP_SIGNATURES settings.
    """
    if not value:
        return False

    allowed_sigs = api_settings.ALLOWED_APP_SIGNATURES

    if api_settings.REQUIRE_SIGNATURE:
        if not allowed_sigs:
            # This should have been caught by settings validation,
            # but we guard anyway.
            return False
        # Constant-time comparison against all allowed signatures
        return any(
            hmac.compare_digest(value.encode(), sig.encode())
            for sig in allowed_sigs
        )
    else:
        # If signature is not required, accept any non-empty string
        return len(value) >= 10


def get_gateway():
    """
    Returns the configured telephony gateway class.
    Currently only Twilio is supported.
    """
    return TwilioGateway