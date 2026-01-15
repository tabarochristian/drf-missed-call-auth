from abc import ABC, abstractmethod


class BaseMissedCallGateway(ABC):
    """
    Abstract base class for missed-call telephony gateways.
    
    All concrete implementations (e.g., Twilio, Plivo, Vonage) must implement 
    the `trigger_missed_call` method and ensure numbers are in E.164 format.
    
    Example implementation:
    
    ```python
    class MyGateway(BaseMissedCallGateway):
        def trigger_missed_call(self, to_number: str, from_number: str) -> bool:
            # Your implementation
            return True
    ```
    """

    @abstractmethod
    def trigger_missed_call(self, to_number: str, from_number: str) -> bool:
        """
        Initiates a missed/flash call from `from_number` to `to_number`.
        
        The implementation should:
        1. Validate both numbers are in E.164 format
        2. Initiate a brief call (1-2 rings) that automatically disconnects
        3. Handle all provider-specific errors gracefully
        4. Return True on success, False on failure
        5. Log all errors appropriately
        
        Args:
            to_number (str): Destination phone number in E.164 format (e.g., +1234567890)
            from_number (str): Source phone number in E.164 format (e.g., +0987654321)
            
        Returns:
            bool: True if the call was successfully initiated, False otherwise.
            
        Raises:
            Should not raise exceptions - return False instead and log errors.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement trigger_missed_call method"
        )