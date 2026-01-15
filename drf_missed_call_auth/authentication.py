from django.utils.translation import gettext_lazy as _
from rest_framework import authentication, exceptions
from .models import MissedCallVerification


class MissedCallSessionAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication for DRF.
    Allows a verified MissedCallVerification session to act as a
    temporary bearer token for subsequent API requests.
    """

    def authenticate(self, request):
        # We look for 'X-MissedCall-Session' in the headers
        session_id = request.META.get('HTTP_X_MISSEDCALL_SESSION')
        if not session_id:
            return None

        try:
            # Fetch the session and ensure it is actually verified
            session = MissedCallVerification.objects.get(
                id=session_id,
                is_verified=True
            )
        except (MissedCallVerification.DoesNotExist, ValueError):
            raise exceptions.AuthenticationFailed(_('Invalid or missing verification session.'))

        # Check for expiry — uses the new `is_expired` property
        if session.is_expired:
            raise exceptions.AuthenticationFailed(_('Verification session has expired.'))

        # In DRF, we return a tuple: (user, auth)
        # Since this is a pre-login phase, request.user will be None,
        # but request.auth will be the session object.
        return (None, session)

    def authenticate_header(self, request):
        return 'X-MissedCall-Session'