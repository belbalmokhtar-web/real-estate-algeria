from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from properties import views  # استيراد views من تطبيق properties

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    # هذا هو المسار الذي يحتاجه القالب
    path('developers/', views.developer_list, name='developer_list'),
    path('accounts/', include('accounts.urls')),
    path('properties/', include('properties.urls')),
    path('rewards/', include('rewards.urls')),
    path('reports/', include('reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
