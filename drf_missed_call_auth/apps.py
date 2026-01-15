from django.apps import AppConfig
from django.core import checks
from django.utils.translation import gettext_lazy as _


def validate_settings(app_configs, **kwargs):
    """
    Django System Check to ensure critical settings are configured.
    Run via: python manage.py check
    """
    from .settings import api_settings
    errors = []

    # 1. Check for Telephony Credentials
    if not api_settings.TWILIO_ACCOUNT_SID or not api_settings.TWILIO_AUTH_TOKEN:
        errors.append(
            checks.Warning(
                _("Twilio credentials are missing."),
                hint=_("Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in your settings or environment variables."),
                id='rfm.W001',
            )
        )

    # 2. Check for App Signature Security
    if api_settings.REQUIRE_SIGNATURE and not getattr(api_settings, 'ALLOWED_APP_SIGNATURES', None):
        errors.append(
            checks.Error(
                _("REQUIRE_SIGNATURE is enabled but no ALLOWED_APP_SIGNATURES are defined."),
                hint=_("Add a list of valid mobile app hashes (e.g., SHA-256) to MISSEDCALL_AUTH['ALLOWED_APP_SIGNATURES']."),
                id='rfm.E001',
            )
        )

    return errors


class MissedCallConfig(AppConfig):
    name = 'rest_framework_missedcall'
    verbose_name = _("Missed Call Verification")
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        """
        Register system checks when the app is ready.
        """
        checks.register(validate_settings, checks.Tags.security)