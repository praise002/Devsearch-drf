from rest_framework.settings import api_settings

class HeaderMixin:
    """
    Mixin to provide get_success_headers method for APIView classes
    """
    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}