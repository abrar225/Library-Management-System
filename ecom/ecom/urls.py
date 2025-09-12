from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

admin.site.site_header = "Bookstore"
admin.site.site_title = "Bookstore Admin Panel"
admin.site.index_title = "Welcome to Bookstore Admin"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app1.urls')),
    path('SiteInfo/', include('SiteInfo.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
