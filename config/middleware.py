from django.shortcuts import render


class MaintenanceModeMiddleware:
    """ميدلوير لوضع الصيانة"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(settings, 'MAINTENANCE_MODE') and settings.MAINTENANCE_MODE:
            return render(request, 'maintenance.html', status=503)
        return self.get_response(request)