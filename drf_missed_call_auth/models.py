import uuid
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from datetime import timedelta

from .managers import CallSourceManager
from .settings import api_settings

class CallSourceNumber(models.Model):
    """
    Represents a physical or virtual number (e.g., Twilio) in the rotation pool.
    """
    phone_number = models.CharField(
        max_length=32, 
        unique=True,
        db_index=True,
        verbose_name=_("phone number"),
        help_text=_("The number in E.164 format used to initiate the missed call.")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("is active"),
        help_text=_("Uncheck this to temporarily remove the number from the pool.")
    )
    label = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_("label"),
        help_text=_("Internal name to identify this specific line (e.g., 'Twilio US 01').")
    )

    objects = CallSourceManager()

    class Meta:
        verbose_name = _("call source number")
        verbose_name_plural = _("call source numbers")

    def __str__(self):
        return f"{self.label or _('Source')} ({self.phone_number})"


class MissedCallVerification(models.Model):
    """
    Tracks an active authentication session. 
    Matches the user's phone + app signature to a specific number from the pool.
    """
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    user_phone = models.CharField(
        max_length=32, 
        db_index=True,
        verbose_name=_("user phone number")
    )
    app_signature = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name=_("application signature"),
        help_text=_("Unique hash identifying the mobile application binary.")
    )
    
    # The 'Target' number the user must report back to the API
    expected_caller = models.ForeignKey(
        CallSourceNumber, 
        on_delete=models.CASCADE,
        related_name='verifications',
        verbose_name=_("expected caller")
    )
    
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_("is verified")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("created at")
    )
    expires_at = models.DateTimeField(
        verbose_name=_("expires at"),
        db_index=True
    )

    class Meta:
        verbose_name = _("missed call verification")
        verbose_name_plural = _("missed call verifications")
        ordering = ['-created_at']
        # Performance: Optimize the two most common lookup patterns
        indexes = [
            models.Index(fields=['user_phone', 'is_verified']),
        ]

    def save(self, *args, **kwargs):
        """
        Auto-calculates the expiration date based on the package settings
        before the record is committed to the database.
        """
        if not self.expires_at:
            self.expires_at = now() + timedelta(seconds=api_settings.VALIDITY_PERIOD)
        super().save(*args, **kwargs)

    @property
    def is_valid(self) -> bool:
        """Checks if the session is still within the validity window and not yet verified."""
        return not self.is_verified and now() < self.expires_at

    def __str__(self):
        return _("Verification for %(phone)s (Expected: %(caller)s)") % {
            'phone': self.user_phone,
            'caller': self.expected_caller.phone_number
        }