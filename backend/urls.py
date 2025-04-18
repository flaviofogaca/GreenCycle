from django.urls import path, include
from core.views import home
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.conf.urls.static import static
from django.conf import settings
# Precisa instalar biblioteca pillow (pip install pillow )

urlpatterns = [
    path('auth/', include('rest_framework.urls')),
    path('v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path(
        'v1/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),
    path('v1/', include('core.urls')),
    path('', home, name='home')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
