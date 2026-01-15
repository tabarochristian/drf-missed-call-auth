from rest_framework.exceptions import APIException
from rest_framework import status
from django.utils.translation import gettext_lazy as _


class TelephonyError(APIException):
    """
    Raised when the telephony provider (e.g., Twilio) fails to send a flash call.
    Typically results in a 503 Service Unavailable response.
    """
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _('Telephony provider is currently unavailable. Please try again later.')
    default_code = 'telephony_unavailable'


class SessionExpired(APIException):
    """
    Raised when a verification session is found but has passed its expiration time.
    Results in a 401 Unauthorized response.
    """
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _('The verification session has expired.')
    default_code = 'session_expired'


class InvalidSignatureError(APIException):
    """
    Raised when the provided app signature does not match any allowed signatures.
    Results in a 403 Forbidden response.
    """
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _('App signature verification failed.')
    default_code = 'invalid_signature'