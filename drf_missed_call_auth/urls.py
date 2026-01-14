from django.urls import path
from .views import MissedCallRequestView, MissedCallVerifyView

# This allows for reverse('rest_framework_missedcall:request')
app_name = 'rest_framework_missedcall'

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