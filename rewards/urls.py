# rewards/urls.py
from django.urls import path
from . import views

app_name = 'rewards'

urlpatterns = [
    path('become-promoter/', views.become_promoter, name='become_promoter'),
    path('become-advertiser/', views.become_advertiser, name='become_advertiser'),
    path('create-link/<int:property_id>/', views.create_affiliate_link, name='create_affiliate_link'),
    path('my-links/', views.my_links, name='my_links'),
    path('my-earnings/', views.my_earnings, name='my_earnings'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('redeem/', views.redeem_points, name='redeem_points'),
    path('click/<str:code>/', views.track_click, name='track_click'),
    path('promoter-dashboard/', views.promoter_dashboard, name='promoter_dashboard'),
    path('advertiser-dashboard/', views.advertiser_dashboard, name='advertiser_dashboard'),
    path('click-duration/', views.click_duration_api, name='click_duration_api'),
    path('reports/', views.dashboard_report, name='reports'),
]