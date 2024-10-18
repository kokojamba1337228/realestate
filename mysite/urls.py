from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin URL path
    path('properties/', include('properties.urls')),
    path('accounts/', include('accounts.urls')),
    path('', include('homepage.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
