import uuid
from datetime import timedelta

from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from .validators import phone_number_validator
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
        help_text=_("The number in E.164 format used to initiate the missed call."),
        validators=[phone_number_validator]
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
        verbose_name=_("user phone number"),
        validators=[phone_number_validator]
    )
    app_signature = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name=_("application signature"),
        help_text=_("Unique hash identifying the mobile application binary.")
    )
    expected_caller = models.ForeignKey(
        CallSourceNumber,
        on_delete=models.CASCADE,
        related_name='verifications',
        verbose_name=_("expected caller")
    )
    
    # Status Fields
    is_verified = models.BooleanField(default=False, verbose_name=_("is verified"))
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name=_("verified at"))
    
    # Security & Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name=_("IP address"))
    attempt_count = models.PositiveSmallIntegerField(default=0, verbose_name=_("attempt count"))
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))
    expires_at = models.DateTimeField(db_index=True, verbose_name=_("expires at"))

    class Meta:
        verbose_name = _("missed call verification")
        verbose_name_plural = _("missed call verifications")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_phone', 'is_verified']),
            models.Index(fields=['expires_at', 'is_verified']), # Optimized for cleanup tasks
        ]

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = now() + timedelta(seconds=api_settings.VALIDITY_PERIOD)
        super().save(*args, **kwargs)

    @property
    def is_expired(self) -> bool:
        return now() >= self.expires_at

    @property
    def is_valid(self) -> bool:
        """
        Checks if the session is still within the validity window, 
        not yet verified, and hasn't exceeded attempt limits.
        """
        max_attempts = getattr(api_settings, 'MAX_VERIFICATION_ATTEMPTS', 3)
        return (
            not self.is_verified and 
            not self.is_expired and 
            self.attempt_count < max_attempts
        )

    @property
    def time_remaining(self):
        """Calculates time remaining for Admin display"""
        if self.is_expired:
            return _("Expired")
        delta = self.expires_at - now()
        minutes, seconds = divmod(int(delta.total_seconds()), 60)
        return f"{minutes:02d}:{seconds:02d}"

    def __str__(self):
        return _("Verification for %(phone)s (Expected: %(caller)s)") % {
            'phone': self.user_phone,
            'caller': self.expected_caller.phone_number
        }