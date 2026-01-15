import os
import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from django.core.exceptions import ValidationError
from ..utils import normalize_phone_number
from .base import BaseMissedCallGateway
from ..settings import api_settings

logger = logging.getLogger(__name__)


class TwilioGateway(BaseMissedCallGateway):
    """
    Production-grade Twilio integration with robust error handling.
    Uses <Reject reason="busy"/> to minimize cost and maximize missed-call reliability.
    """

    def __init__(self):
        self._client = None
        # Prefer settings, fallback to environment variables
        self.account_sid = (
            api_settings.TWILIO_ACCOUNT_SID or os.getenv('TWILIO_ACCOUNT_SID')
        )
        self.auth_token = (
            api_settings.TWILIO_AUTH_TOKEN or os.getenv('TWILIO_AUTH_TOKEN')
        )

    @property
    def client(self):
        """Lazy-load the Twilio client only when needed."""
        if self._client is None:
            try:
                if not self.account_sid or not self.auth_token:
                    logger.error(
                        "Twilio credentials missing. "
                        "Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in settings or environment."
                    )
                    return None
                self._client = Client(self.account_sid, self.auth_token)
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}", exc_info=True)
                return None
        return self._client

    def clean_number(self, number: str) -> str:
        """
        Ensures the number is in E.164 format.
        Reuses the global normalizer and validates structure.
        """
        cleaned = normalize_phone_number(number)
        if not cleaned.startswith('+') or len(cleaned) < 10:
            raise ValidationError(f"Invalid phone number format: {number}")
        return cleaned

    def trigger_missed_call(self, to_number: str, from_number: str) -> bool:
        """
        Triggers a flash call using <Reject reason="busy"/>.
        This is often free and results in a faster missed-call notification.
        """
        if not self.client:
            return False

        try:
            to_clean = self.clean_number(to_number)
            from_clean = self.clean_number(from_number)

            call = self.client.calls.create(
                to=to_clean,
                from_=from_clean,
                twiml='<Response><Reject reason="busy"/></Response>',
                timeout=10
            )
            logger.debug(f"Missed call initiated: {call.sid} from {from_clean} to {to_clean}")
            return True

        except TwilioRestException as e:
            logger.error(
                f"Twilio API error (code {e.code}): {e.msg} | To: {to_number}, From: {from_number}"
            )
            return False
        except ValidationError as e:
            logger.error(f"Phone number validation failed: {e.message}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in Twilio gateway: {e}", exc_info=True)
            return False