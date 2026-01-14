from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import MissedCallVerification, CallSourceNumber
from .utils import normalize_phone_number, validate_app_signature, get_gateway
from .settings import api_settings

class MissedCallRequestSerializer(serializers.Serializer):
    """
    Handles the initiation of a flash call.
    Validates the app binary and selects an available line from the pool.
    """
    phone_number = serializers.CharField(max_length=32)
    app_signature = serializers.CharField(max_length=255)

    def validate_phone_number(self, value):
        return normalize_phone_number(value)

    def validate(self, attrs):
        # 1. Security Check: Validate App Signature
        if not validate_app_signature(attrs['app_signature']):
            # Use a generic error for security to prevent fingerprinting
            raise serializers.ValidationError(_("Request could not be authorized."))
        
        # 2. Pool Selection Logic
        pool_manager = CallSourceNumber.objects
        
        # Performance: Get last used caller for this phone to avoid repeat usage
        last_caller_id = MissedCallVerification.objects.filter(
            user_phone=attrs['phone_number']
        ).values_list('expected_caller__phone_number', flat=True).first()
        
        caller = pool_manager.get_random_sender(exclude_number=last_caller_id)

        if not caller:
            raise serializers.ValidationError(_("Verification service is temporarily unavailable."))

        attrs['chosen_caller'] = caller
        return attrs

    def create(self, validated_data):
        """
        Atomically creates a session and triggers the gateway.
        """
        try:
            with transaction.atomic():
                verification = MissedCallVerification.objects.create(
                    user_phone=validated_data['phone_number'],
                    app_signature=validated_data['app_signature'],
                    expected_caller=validated_data['chosen_caller']
                )
                
                gateway = get_gateway()
                call_sent = gateway.trigger_missed_call(
                    to_number=verification.user_phone,
                    from_number=verification.expected_caller.phone_number
                )

                if not call_sent:
                    # Triggering a manual exception to rollback the DB transaction
                    raise Exception("Telephony provider failed to initiate call.")
                
                return verification
        except Exception as e:
            # For production, we raise a user-friendly error
            raise serializers.ValidationError(_("Could not initiate verification call. Please try again."))


class MissedCallVerifySerializer(serializers.Serializer):
    """
    Handles the 'Zero-Code' confirmation.
    Compares the number detected by the app with the number assigned by the server.
    """
    phone_number = serializers.CharField(max_length=32)
    received_caller_id = serializers.CharField(max_length=32)

    def validate(self, attrs):
        phone = normalize_phone_number(attrs['phone_number'])
        caller_id = normalize_phone_number(attrs['received_caller_id'])

        # Find the specific pending session
        session = MissedCallVerification.objects.filter(
            user_phone=phone,
            is_verified=False
        ).order_by('-created_at').first()

        if not session or not session.is_valid:
            raise serializers.ValidationError(_("No active verification session found."))

        # Strict Caller ID Match
        if session.expected_caller.phone_number != caller_id:
            raise serializers.ValidationError(_("Verification failed. Incorrect caller identified."))

        attrs['session'] = session
        return attrs

    def update(self, instance, validated_data):
        """Marks the session as verified."""
        instance.is_verified = True
        instance.save()
        return instance