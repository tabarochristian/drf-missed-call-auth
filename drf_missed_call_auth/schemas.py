from rest_framework.schemas.openapi import AutoSchema

class MissedCallSchema(AutoSchema):
    """
    Custom schema to ensure Verification endpoints are clearly documented
    in Swagger/Redoc.
    """
    def get_operation(self, path, method):
        operation = super().get_operation(path, method)
        if 'request' in path:
            operation['summary'] = 'Initiate Flash Call'
            operation['description'] = 'Triggers a missed call to the user phone.'
        elif 'verify' in path:
            operation['summary'] = 'Confirm Caller ID'
            operation['description'] = 'Validates the intercepted number.'
        return operation