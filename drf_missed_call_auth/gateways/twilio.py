import logging
from django.utils.translation import gettext as _
from .base import BaseMissedCallGateway
from ..settings import api_settings

logger = logging.getLogger(__name__)

class TwilioGateway(BaseMissedCallGateway):
    """
    Production-grade Twilio integration with robust error handling.
    """

    def __init__(self):
        self._client = None
        self.account_sid = api_settings.TWILIO_ACCOUNT_SID
        self.auth_token = api_settings.TWILIO_AUTH_TOKEN

    @property
    def client(self):
        """Lazy-load the Twilio client only when needed."""
        if self._client is None:
            try:
                from twilio.rest import Client
                if not self.account_sid or not self.auth_token:
                    logger.error(_("Twilio credentials are not configured in REST_FRAMEWORK_MISSEDCALL settings."))
                    return None
                self._client = Client(self.account_sid, self.auth_token)
            except ImportError:
                logger.error(_("The 'twilio' package is required. Install it via 'pip install twilio'."))
                return None
        return self._client

    def trigger_missed_call(self, to_number: str, from_number: str) -> bool:
        """
        Triggers a flash call. 
        Uses <Reject/> which signals 'Busy' to the carrier, 
        often resulting in a faster 'Missed Call' notification than <Hangup/>.
        """
        if not self.client:
            return False

        try:
            self.client.calls.create(
                to=self.clean_number(to_number),
                from_=self.clean_number(from_number),
                # 'Reject' is often free as it doesn't 'answer' the line
                twiml='<Response><Reject reason="busy" /></Response>',
                timeout=10 
            )
            return True
        except Exception as e:
            logger.error(
                _("Twilio Flash Call Failed: %(error)s") % {'error': str(e)},
                exc_info=True # Includes stack trace in logs for easier debugging
            )
            return False