from django.urls import path
from . import views

urlpatterns = [
    path('shop/<int:server_id>/', views.shop, name='shop'),
    path('buy_sms/', views.buy_sms, name='buy_sms'),
    path('buy_other/', views.buy_other, name='buy_other'),
    path('lvlup_check', views.lvlup_check, name='lvlup_check'),
    path('use_voucher/', views.use_voucher, name='use_voucher'),
    path('success/', views.success_page, name='success_page'),
]
