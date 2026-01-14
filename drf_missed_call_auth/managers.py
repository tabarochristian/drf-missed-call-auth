import random
from typing import Optional, TYPE_CHECKING
from django.db import models
from django.utils.translation import gettext as _

if TYPE_CHECKING:
    from .models import CallSourceNumber

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

    def get_random_sender(self, exclude_number: str = None) -> Optional['CallSourceNumber']:
        """
        Picks a random sender from the available pool using an optimized 
        database-friendly selection strategy.
        
        Args:
            exclude_number (str): Optional E.164 number to exclude (usually the last used).

        Returns:
            Optional[CallSourceNumber]: A random number instance or None if pool is empty.
        """
        queryset = self.get_active_pool()

        if exclude_number:
            filtered_queryset = queryset.exclude(phone_number=exclude_number)
            # Only use filtered queryset if it doesn't leave us with an empty pool
            if filtered_queryset.exists():
                queryset = filtered_queryset

        count = queryset.count()
        if count == 0:
            # No numbers available in the pool. 
            # High-level implementation should log this for the admin.
            return None

        # PERFORMANCE OPTIMIZATION:
        # Instead of list(queryset), we pick a random index and use array slicing.
        # This results in a LIMIT 1 OFFSET X query, which is extremely fast.
        random_index = random.randint(0, count - 1)
        return queryset[random_index]