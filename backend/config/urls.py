from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve
from rest_framework_simplejwt.views import TokenBlacklistView
from management.views import ThrottledTokenObtainPairView, ThrottledTokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("management.urls")),
    path("api/auth/token/", ThrottledTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", ThrottledTokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
]

# Uploaded media (user/car/passport photos, etc.) has no dedicated static
# file server in front of it — unlike STATIC_ROOT, which WhiteNoise serves
# regardless of DEBUG (see settings.py), `django.conf.urls.static.static()`
# refuses to register a route unless DEBUG=True, which left every uploaded
# file 404ing in production. Wired up directly via the underlying view
# instead, bypassing that DEBUG gate. Gunicorn serving media itself isn't
# as efficient as a dedicated nginx `location /media/` block would be, but
# it's correct, and this app's media volume is nowhere near the traffic
# where that would matter.
urlpatterns += [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]

