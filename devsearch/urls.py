from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# from django.http import JsonResponse
# def handler404(request, exception=None):
#     response = JsonResponse({"status": "failure", "message": "Not Found"})
#     response.status_code = 404
#     return response


# def handler500(request, exception=None):
#     response = JsonResponse({"status": "failure", "message": "Server Error"})
#     response.status_code = 500
#     return response


# handler404 = handler404
# handler500 = handler500

urlpatterns = [
    path("admin/", admin.site.urls),
    path("__debug__/", include("debug_toolbar.urls")),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/profiles/", include("apps.profiles.urls")),
    path("api/v1/projects/", include("apps.projects.urls")),
    path("api/v1/messages/", include("apps.messaging.urls")),
    
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
