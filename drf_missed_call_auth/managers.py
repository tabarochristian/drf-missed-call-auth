from .models import CallSourceNumber
from django.db import models
from typing import Optional


class CallSourceManager(models.Manager):
    """
    Custom manager for CallSourceNumber to handle high-performance 
    selection logic for the number pool.
    """

    def get_active_pool(self) -> models.QuerySet:
        """
        Returns a QuerySet of numbers marked as active.
        """
        return self.filter(is_active=True)

    def get_random_sender(self, exclude_number: Optional[str] = None) -> Optional['CallSourceNumber']:
        """
        Picks a random active sender from the pool.
        
        If `exclude_number` is provided (e.g., the last used number), 
        it will be excluded to prevent immediate reuse—improving user experience 
        and reducing carrier filtering risk.

        Returns:
            A random CallSourceNumber instance, or None if no active numbers are available.
        """
        queryset = self.get_active_pool()
        if exclude_number:
            queryset = queryset.exclude(phone_number=exclude_number)
        return queryset.order_by('?').first()