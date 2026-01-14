from django.dispatch import Signal

# Sent when a flash call is successfully triggered via the provider
missed_call_sent = Signal() # args: [verification_instance]

# Sent when a user successfully verifies the Caller ID
verification_success = Signal() # args: [verification_instance]

# Sent when a verification attempt fails (e.g., wrong number)
verification_failed = Signal() # args: [phone_number, expected, received]