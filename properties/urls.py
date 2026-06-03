# properties/urls.py
from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    # الصفحات الرئيسية
    path('', views.home, name='home'),
    path('list/', views.property_list, name='property_list'),
    path('detail/<int:id>/', views.property_detail, name='property_detail'),

    # إدارة العقارات
    path('create/', views.property_create, name='property_create'),
    path('edit/<int:id>/', views.property_edit, name='property_edit'),
    path('delete/<int:id>/', views.property_delete, name='property_delete'),
    path('toggle-favorite/<int:property_id>/', views.toggle_favorite, name='toggle_favorite'),

    # المطورين العقاريين (Promoteurs)
    path('promoteurs/', views.promoteur_list, name='promoteur_list'),
    path('promoteurs/<int:pk>/', views.promoteur_detail, name='promoteur_detail'),
    path('promoteurs/<int:pk>/contact/', views.contact_promoteur, name='contact_promoteur'),
    path('developers/', views.developer_list, name='developer_list_global'),

    # مشاريع المطورين
    path('projets/<int:pk>/', views.projet_detail, name='projet_detail'),

    # التقييم العقاري
    path('valuation/', views.valuation_view, name='valuation'),
    path('get-communes/', views.get_communes, name='get_communes'),
    path('get-characteristics/', views.get_characteristics, name='get_characteristics'),
    path('get-zone-range/', views.get_zone_range, name='get_zone_range'),
    path('get-valuation-result/', views.get_valuation_result, name='get_valuation_result'),

    # API المشاريع
    path('api/projet/<int:pk>/', views.api_projet_detail, name='api_projet_detail'),

    # دوال الاختبار
    path('promoteurs-simple/', views.promoteur_list_simple, name='promoteur_list_simple'),
    path('promoteurs-test/', views.promoteur_list_test, name='promoteur_list_test'),
    path('map/', views.property_map, name='property_map'),
]
