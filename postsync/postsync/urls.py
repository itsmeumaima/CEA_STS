from django.contrib import admin
from django.urls import path,include
from core.views import contact, index
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('item/',include('item.urls')),
    path('admin/', admin.site.urls),
    path('dashboard/',include('dashboard.urls')),
    path('', include('core.urls')),
    path('cart/', include('cart.urls')),
    path('analytics/', include('analytics.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
