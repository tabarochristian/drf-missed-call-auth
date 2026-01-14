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
    # Defaulting to AnonRateThrottle; developers can override this in settings
    throttle_classes = [AnonRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            serializer.save()
            return Response(
                {"detail": _("Flash call initiated. Please observe incoming calls.")},
                status=status.HTTP_202_ACCEPTED
            )
        except Exception as e:
            logger.error(f"Flash call request failed: {str(e)}")
            return Response(
                {"error": _("Service temporarily unavailable. Please try again later.")},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
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
        
        # Mark as verified and get the session object
        session = serializer.save()
        
        return self.get_success_response(session)

    def get_success_response(self, session):
        """
        Hook for developers to customize the response. 
        Usually overridden to return a JWT or DRF Token.
        """
        data = {
            "detail": _("Verification successful."),
            "phone_number": session.user_phone,
            "verified": True
        }
        
        # Optional: Integration with DRF Authtoken if configured
        if api_settings.TOKEN_MODEL:
            # Note: Developer needs to handle User creation/lookup logic
            # This is a placeholder for where the token would be injected.
            data["token"] = "..." 

        return Response(data, status=status.HTTP_200_OK)