# reports/urls.py
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.dashboard_report, name='dashboard'),  # هذا سيجعل الصفحة على /reports/
    # أو
    # path('dashboard/', views.dashboard_report, name='dashboard'),
]