from rest_framework import permissions

class IsMissedCallVerified(permissions.BasePermission):
    """
    Allows access only to users who have a verified, non-expired session.
    Expects 'X-MissedCall-Session' header.
    """
    def has_permission(self, request, view):
        session_id = request.headers.get('X-MissedCall-Session')
        if not session_id:
            return False
            
        from .models import MissedCallVerification
        return MissedCallVerification.objects.filter(
            id=session_id, 
            is_verified=True
        ).exists()