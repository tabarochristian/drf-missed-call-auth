from abc import ABC, abstractmethod
from typing import Optional
from django.utils.translation import gettext as _
from ..settings import api_settings

class BaseMissedCallGateway(ABC):
    """
    Interface for telephony providers. 
    Enforces a consistent contract for triggering flash calls.
    """

    @abstractmethod
    def trigger_missed_call(self, to_number: str, from_number: str) -> bool:
        """
        Initiates the missed call.
        Returns True on success, False on failure.
        """
        pass

    def clean_number(self, phone_number: str) -> str:
        """Ensures the number is stripped of non-numeric characters except '+'."""
        return "+" + "".join(filter(str.isdigit, phone_number))