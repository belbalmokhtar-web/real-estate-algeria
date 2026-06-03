# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # مسارات المصادقة
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),

    # مسارات الملف الشخصي
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),

    # مسارات الوكلاء والمطورين
    path('agents/', views.agent_list, name='agent_list'),
    path('developers/', views.developer_list, name='developer_list'),
    path('agent/<int:agent_id>/', views.agent_detail, name='agent_detail'),
    path('developer/<str:username>/', views.developer_detail, name='developer_detail'),

    # مسارات الرسائل
    path('inbox/', views.inbox, name='inbox'),
    path('compose/', views.compose_message, name='compose_message'),
    path('compose/<int:recipient_id>/', views.compose_message, name='compose_message_with_recipient'),
    path('compose/<int:recipient_id>/<int:property_id>/', views.compose_message, name='compose_message_with_property'),
    path('message/<int:message_id>/', views.view_message, name='view_message'),

    # مسارات المفضلة
    path('favorites/', views.favorites_list, name='favorites_list'),
]