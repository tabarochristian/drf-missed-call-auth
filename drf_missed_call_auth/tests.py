from django.test import TestCase, override_settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import timedelta
from unittest.mock import patch, MagicMock
import uuid

from .models import CallSourceNumber, MissedCallVerification
from .utils import normalize_phone_number, validate_app_signature
from .settings import api_settings

User = get_user_model()


class PhoneNumberNormalizationTests(TestCase):
    """Test phone number normalization"""
    
    def test_already_normalized(self):
        """Test already normalized E.164 number"""
        result = normalize_phone_number('+1234567890')
        self.assertEqual(result, '+1234567890')
    
    def test_with_spaces(self):
        """Test number with spaces"""
        result = normalize_phone_number('+1 234 567 890')
        self.assertEqual(result, '+1234567890')
    
    def test_with_dashes(self):
        """Test number with dashes"""
        result = normalize_phone_number('+1-234-567-890')
        self.assertEqual(result, '+1234567890')
    
    def test_with_parentheses(self):
        """Test number with parentheses"""
        result = normalize_phone_number('+1 (234) 567-890')
        self.assertEqual(result, '+1234567890')
    
    def test_too_short(self):
        """Test too short number"""
        with self.assertRaises(ValueError):
            normalize_phone_number('+123')
    
    def test_too_long(self):
        """Test too long number"""
        with self.assertRaises(ValueError):
            normalize_phone_number('+' + '1' * 20)
    
    def test_empty_number(self):
        """Test empty number"""
        with self.assertRaises(ValueError):
            normalize_phone_number('')


@override_settings(
    MISSEDCALL_AUTH={
        'REQUIRE_SIGNATURE': True,
        'ALLOWED_APP_SIGNATURES': ['test-signature-123'],
        'VALIDITY_PERIOD': 300,
    }
)
class AppSignatureValidationTests(TestCase):
    """Test app signature validation"""
    
    def test_valid_signature(self):
        """Test valid signature"""
        result = validate_app_signature('test-signature-123')
        self.assertTrue(result)
    
    def test_invalid_signature(self):
        """Test invalid signature"""
        result = validate_app_signature('invalid-signature')
        self.assertFalse(result)
    
    def test_empty_signature(self):
        """Test empty signature"""
        result = validate_app_signature('')
        self.assertFalse(result)
    
    @override_settings(
        MISSEDCALL_AUTH={
            'REQUIRE_SIGNATURE': False,
        }
    )
    def test_signature_not_required(self):
        """Test when signature is not required"""
        result = validate_app_signature('any-signature-here')
        self.assertTrue(result)


class CallSourceNumberTests(TestCase):
    """Test CallSourceNumber model"""
    
    def setUp(self):
        self.number1 = CallSourceNumber.objects.create(
            phone_number='+1234567890',
            label='Test Number 1',
            is_active=True
        )
        self.number2 = CallSourceNumber.objects.create(
            phone_number='+0987654321',
            label='Test Number 2',
            is_active=True
        )
        self.number3 = CallSourceNumber.objects.create(
            phone_number='+1111111111',
            label='Inactive Number',
            is_active=False
        )
    
    def test_get_active_pool(self):
        """Test getting active numbers"""
        active = CallSourceNumber.objects.get_active_pool()
        self.assertEqual(active.count(), 2)
        self.assertIn(self.number1, active)
        self.assertIn(self.number2, active)
        self.assertNotIn(self.number3, active)
    
    def test_get_random_sender(self):
        """Test getting random sender"""
        sender = CallSourceNumber.objects.get_random_sender()
        self.assertIsNotNone(sender)
        self.assertTrue(sender.is_active)
    
    def test_get_random_sender_with_exclusion(self):
        """Test getting random sender with exclusion"""
        sender = CallSourceNumber.objects.get_random_sender(
            exclude_number='+1234567890'
        )
        self.assertIsNotNone(sender)
        self.assertNotEqual(sender.phone_number, '+1234567890')
    
    def test_phone_number_validation(self):
        """Test phone number validation"""
        with self.assertRaises(Exception):
            number = CallSourceNumber(
                phone_number='invalid',
                label='Invalid'
            )
            number.save()


class MissedCallVerificationTests(TestCase):
    """Test MissedCallVerification model"""
    
    def setUp(self):
        self.caller = CallSourceNumber.objects.create(
            phone_number='+1234567890',
            is_active=True
        )
    
    def test_create_verification(self):
        """Test creating verification"""
        verification = MissedCallVerification.objects.create(
            user_phone='+0987654321',
            app_signature='test-signature',
            expected_caller=self.caller
        )
        self.assertIsNotNone(verification.id)
        self.assertFalse(verification.is_verified)
        self.assertIsNotNone(verification.expires_at)
    
    def test_is_valid_property(self):
        """Test is_valid property"""
        verification = MissedCallVerification.objects.create(
            user_phone='+0987654321',
            app_signature='test-signature',
            expected_caller=self.caller
        )
        self.assertTrue(verification.is_valid)
    
    def test_is_expired_property(self):
        """Test is_expired property"""
        past_time = timezone.now() - timedelta(hours=1)
        verification = MissedCallVerification.objects.create(
            user_phone='+0987654321',
            app_signature='test-signature',
            expected_caller=self.caller,
            expires_at=past_time
        )
        self.assertTrue(verification.is_expired)
    
    def test_time_remaining(self):
        """Test time_remaining property"""
        verification = MissedCallVerification.objects.create(
            user_phone='+0987654321',
            app_signature='test-signature',
            expected_caller=self.caller
        )
        remaining = verification.time_remaining
        self.assertGreater(remaining.total_seconds(), 0)
    
    def test_increment_attempt(self):
        """Test incrementing attempt counter"""
        verification = MissedCallVerification.objects.create(
            user_phone='+0987654321',
            app_signature='test-signature',
            expected_caller=self.caller
        )
        self.assertEqual(verification.attempt_count, 0)
        
        verification.increment_attempt()
        self.assertEqual(verification.attempt_count, 1)
        
        verification.increment_attempt()
        self.assertEqual(verification.attempt_count, 2)


@override_settings(
    MISSEDCALL_AUTH={
        'REQUIRE_SIGNATURE': False,
        'VALIDITY_PERIOD': 300,
        'MAX_ATTEMPTS_PER_DAY': 10,
        'TWILIO_ACCOUNT_SID': 'test',
        'TWILIO_AUTH_TOKEN': 'test',
    }
)
class MissedCallAPITests(APITestCase):
    """Test API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.caller = CallSourceNumber.objects.create(
            phone_number='+1234567890',
            is_active=True
        )
    
    @patch('drf_missed_call_auth.gateways.twilio.TwilioGateway.trigger_missed_call')
    def test_request_endpoint(self, mock_trigger):
        """Test request endpoint"""
        mock_trigger.return_value = True
        
        data = {
            'phone_number': '+0987654321',
            'app_signature': 'test-signature'
        }
        
        response = self.client.post('/auth/request/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn('session_id', response.data)
        self.assertIn('expires_at', response.data)
    
    @patch('drf_missed_call_auth.gateways.twilio.TwilioGateway.trigger_missed_call')
    def test_request_with_invalid_phone(self, mock_trigger):
        """Test request with invalid phone"""
        data = {
            'phone_number': 'invalid',
            'app_signature': 'test-signature'
        }
        
        response = self.client.post('/auth/request/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('drf_missed_call_auth.gateways.twilio.TwilioGateway.trigger_missed_call')
    def test_verify_endpoint_success(self, mock_trigger):
        """Test successful verification"""
        mock_trigger.return_value = True
        
        # First create a session
        verification = MissedCallVerification.objects.create(
            user_phone='+0987654321',
            app_signature='test-signature',
            expected_caller=self.caller
        )
        
        # Then verify it
        data = {
            'phone_number': '+0987654321',
            'received_caller_id': '+1234567890'
        }
        
        response = self.client.post('/auth/verify/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['verified'])
        
        # Check verification was marked as verified
        verification.refresh_from_db()
        self.assertTrue(verification.is_verified)
    
    def test_verify_endpoint_wrong_caller(self):
        """Test verification with wrong caller ID"""
        verification = MissedCallVerification.objects.create(
            user_phone='+0987654321',
            app_signature='test-signature',
            expected_caller=self.caller
        )
        
        data = {
            'phone_number': '+0987654321',
            'received_caller_id': '+9999999999'  # Wrong number
        }
        
        response = self.client.post('/auth/verify/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_verify_endpoint_no_session(self):
        """Test verification without existing session"""
        data = {
            'phone_number': '+0987654321',
            'received_caller_id': '+1234567890'
        }
        
        response = self.client.post('/auth/verify/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_status_endpoint(self):
        """Test status endpoint"""
        verification = MissedCallVerification.objects.create(
            user_phone='+0987654321',
            app_signature='test-signature',
            expected_caller=self.caller
        )
        
        response = self.client.get(f'/auth/status/{verification.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_verified', response.data)
        self.assertIn('is_expired', response.data)
        self.assertIn('time_remaining_seconds', response.data)


class CleanupCommandTests(TestCase):
    """Test cleanup management command"""
    
    def setUp(self):
        self.caller = CallSourceNumber.objects.create(
            phone_number='+1234567890',
            is_active=True
        )
    
    def test_cleanup_old_sessions(self):
        """Test cleaning up old expired sessions"""
        # Create old expired session
        old_time = timezone.now() - timedelta(days=10)
        old_verification = MissedCallVerification.objects.create(
            user_phone='+0987654321',
            app_signature='test-signature',
            expected_caller=self.caller,
            expires_at=old_time
        )
        
        # Create recent session
        recent_verification = MissedCallVerification.objects.create(
            user_phone='+1111111111',
            app_signature='test-signature',
            expected_caller=self.caller
        )
        
        # Run cleanup
        deleted_count, _ = MissedCallVerification.cleanup_expired(days_old=7)
        
        # Old session should be deleted
        self.assertFalse(
            MissedCallVerification.objects.filter(id=old_verification.id).exists()
        )
        
        # Recent session should remain
        self.assertTrue(
            MissedCallVerification.objects.filter(id=recent_verification.id).exists()
        )