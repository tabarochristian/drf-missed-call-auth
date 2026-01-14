from django.conf import settings
from django.test.signals import setting_changed
from rest_framework.settings import APISettings as _APISettings

# The key that developers will use in their Django settings.py
USER_SETTINGS = getattr(settings, 'REST_FRAMEWORK_MISSEDCALL', None)

# Intelligent defaults for a zero-effort flash-call flow
DEFAULTS = {
    # GATEWAY: The class that interacts with Twilio/Provider APIs
    'GATEWAY_CLASS': 'rest_framework_missedcall.gateways.twilio.TwilioGateway',
    
    # POOL: The strategy for picking the next caller ('random' or 'round_robin')
    'POOL_STRATEGY': 'random',
    
    # SECURITY: Whether the phone signature is mandatory for every request
    # This identifies the mobile app binary (Android/iOS)
    'REQUIRE_SIGNATURE': True,
    
    # TIMEOUT: Seconds before the missed call verification session expires
    # Usually short (e.g., 2 minutes) because flash calls are near-instant
    'VALIDITY_PERIOD': 120,
    
    # AUTH: The model used to generate tokens upon successful verification
    'TOKEN_MODEL': 'rest_framework.authtoken.models.Token',
    
    # PROVIDER CONFIG: Placeholders for Twilio credentials
    'TWILIO_ACCOUNT_SID': None,
    'TWILIO_AUTH_TOKEN': None,
}

# List of settings that are classes or modules (importable strings)
# This allows developers to swap components without touching package code
IMPORT_STRINGS = [
    'GATEWAY_CLASS',
    'TOKEN_MODEL',
]

class APISettings(_APISettings):
    """
    Internal settings class that handles lazy loading and string imports.
    Mirroring the official DRF settings architecture.
    """
    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError(
                f"Invalid setting: '{attr}'. Please check your 'REST_FRAMEWORK_MISSEDCALL' "
                f"configuration in settings.py or refer to the package documentation."
            )
        return super().__getattr__(attr)

# Initialize the settings object for the package
api_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)

def reload_api_settings(*args, **kwargs):
    """
    Enables dynamic updates to settings, crucial for high-level 
    testing environments and @override_settings decorators.
    """
    global api_settings
    setting = kwargs.get('setting')
    if setting == 'REST_FRAMEWORK_MISSEDCALL':
        api_settings = APISettings(kwargs.get('value'), DEFAULTS, IMPORT_STRINGS)

setting_changed.connect(reload_api_settings)