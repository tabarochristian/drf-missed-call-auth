from django.urls import path
from .views import (
    MissedCallRequestView, 
    MissedCallVerifyView,
    MissedCallStatusView
)
from .settings import api_settings

# This allows for reverse('drf_missed_call_auth:request')
app_name = 'drf_missed_call_auth'

urlpatterns = [
    path(
        'request/', 
        MissedCallRequestView.as_view(), 
        name='request'
    ),
    path(
        'verify/', 
        MissedCallVerifyView.as_view(), 
        name='verify'
    ),
]

# Conditionally add status endpoint
if api_settings.ENABLE_STATUS_ENDPOINT:
    urlpatterns.append(
        path(
            'status/<uuid:session_id>/',
            MissedCallStatusView.as_view(),
            name='status'
        )
    )