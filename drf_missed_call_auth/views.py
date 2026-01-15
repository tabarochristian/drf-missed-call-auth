import logging
from django.utils.translation import gettext_lazy as _
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle
from .serializers import MissedCallRequestSerializer, MissedCallVerifySerializer
from .settings import api_settings

logger = logging.getLogger(__name__)


class MissedCallRequestView(generics.GenericAPIView):
    """
    Initiates a flash-call verification session.
    Throttling is highly recommended to prevent Twilio credit exhaustion.
    """
    serializer_class = MissedCallRequestSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Let DRF's exception handler manage telephony or DB errors
        verification = serializer.save()
        return Response(
            {"detail": _("Flash call initiated. Please observe incoming calls.")},
            status=status.HTTP_202_ACCEPTED
        )


class MissedCallVerifyView(generics.GenericAPIView):
    """
    Confirms the flash-call by matching the reported Caller ID.
    On success, this view provides a hook to return authentication tokens.
    """
    serializer_class = MissedCallVerifySerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = serializer.save()  # Marks as verified and emits signal
        return self.get_success_response(session)

    def get_success_response(self, session):
        """
        Hook for developers to customize the response.
        Override this method to:
        - Link phone to a User model
        - Generate JWT / DRF Token
        - Return custom claims

        Example:
            from rest_framework.authtoken.models import Token
            user = get_or_create_user_from_phone(session.user_phone)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key})
        """
        data = {
            "detail": _("Verification successful."),
            "phone_number": session.user_phone,
            "verified": True
        }

        # Optional: Indicate that token integration is possible if configured
        if api_settings.TOKEN_MODEL:
            # Do NOT generate a token here — no User exists yet.
            # This is just a hint for developers.
            pass

        return Response(data, status=status.HTTP_200_OK)