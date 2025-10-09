from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cadastros/', include('cadastros.urls')),
    path('coordenacao/', include('coordenacao.urls')),
    path('comunicacao/', include('comunicacao.urls')),
    path('', include('landing.urls')),
    path('dados/', include('dados.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)