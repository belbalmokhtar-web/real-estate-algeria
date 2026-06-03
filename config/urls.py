from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from properties.views import home  # استيراد home من views الخاصة بالعقارات
from accounts import views as accounts_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('properties/', include('properties.urls')),
    path('rewards/', include('rewards.urls')),
    path('properties/', include('properties.urls', namespace='properties')),
    path('', home, name='home'),  # الصفحة الرئيسية
    path('reports/', include('reports.urls')),

    # تحويل المسار القديم /developers/ إلى المسار الجديد /properties/promoteurs/
    path('developers/', RedirectView.as_view(url='/properties/promoteurs/', permanent=True),
         name='developer_list_global'),

]

if settings.DEBUG:  # ← بدون مسافات إضافية، محاذي تماماً لليسار
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



