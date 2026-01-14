# Django REST Framework Missed Call

**The most cost-effective authentication gateway for mobile apps.** Stop paying for expensive international SMS OTPs. `drf-missedcall` implements a **Zero-Code** authentication flow: the server triggers a brief "Flash Call," and your mobile app automatically verifies the incoming Caller ID.

---

## 🚀 The "Zero-Code" Flow

1. **Initiate**: The mobile app sends the user's phone number and a unique App Signature to the `/request/` endpoint.
2. **Trigger**: The server selects a random number from your managed pool and triggers a brief call (1-2 rings) via Twilio or a custom gateway.
3. **Intercept**: The mobile app detects the incoming call (via `BroadcastReceiver` on Android or `CallKit` on iOS), extracts the Caller ID, and rejects/hangs up the call immediately.
4. **Finalize**: The app sends the extracted Caller ID back to the `/verify/` endpoint. If it matches, the server returns a verified session or auth token.

---

## 🛠 Installation

```bash
pip install django-rest-framework-missedcall

```

Add to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'rest_framework_missedcall',
]

```

Run migrations to create the session and number pool tables:

```bash
python manage.py migrate

```

---

## ⚙️ Configuration

This package includes built-in **Django System Checks**. Your settings are validated on server startup to prevent production misconfigurations.

```python
REST_FRAMEWORK_MISSEDCALL = {
    'TWILIO_ACCOUNT_SID': 'AC...',
    'TWILIO_AUTH_TOKEN': 'your_token',
    'REQUIRE_SIGNATURE': True,
    'ALLOWED_APP_SIGNATURES': ['my-app-hash-123'],  # Recommended for security
    'SESSION_EXPIRY_MINUTES': 2,
    'GATEWAY_CLASS': 'rest_framework_missedcall.gateways.TwilioGateway',
}

```

---

## 🔌 Advanced Usage

### Signal Hooks

Leverage Django Signals to trigger post-verification logic, such as automatic user registration or fraud logging.

```python
from django.dispatch import receiver
from rest_framework_missedcall.signals import verification_success

@receiver(verification_success)
def handle_new_user(sender, instance, **kwargs):
    # instance is a MissedCallVerification object
    user_phone = instance.user_phone
    # Your logic to log in or register the user
    pass

```

### Smart Number Pooling

The library includes a `CallSourceNumber` model. You can manage your telephony numbers via the Django Admin. The `CallSourceManager` uses an intelligent randomization logic to ensure that a user is rarely called by the same number twice in a row, significantly increasing the security of the flash-call intercept.

---

## 🛡 Security & Best Practices

* **Timing Attack Prevention**: Signature checks use `constant_time_compare` to prevent side-channel attacks.
* **Atomic Transactions**: Telephony triggers are wrapped in database transactions; if the call fails to trigger, the session is never created.
* **Rate Limiting**: Fully compatible with DRF's `AnonRateThrottle` to protect your telephony credits from brute-force attempts.
* **Replay Protection**: Verification IDs are UUIDs and sessions are strictly one-time use with a short TTL.

---

## 🤝 Contributing

Contributions are welcome! If you find a bug or have a feature request, please open an issue or submit a pull request.

---

Built with ❤️ by [tabaro](https://www.google.com/search?q=https://github.com/tabaro)