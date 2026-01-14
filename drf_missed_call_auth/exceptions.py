from rest_framework.exceptions import APIException
from rest_framework import status
from django.utils.translation import gettext_lazy as _

class TelephonyError(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _('Telephony provider is currently unavailable. Please try again later.')
    default_code = 'telephony_unavailable'

class SessionExpired(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _('The verification session has expired.')
    default_code = 'session_expired'

class InvalidSignatureError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _('App signature verification failed.')
    default_code = 'invalid_signature'