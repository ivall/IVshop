from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('oauth_callback/', views.callback, name='callback'),
    path('logout/', views.logout, name='logout'),
    path('add_server/', views.add_server, name='add_server'),
    path('panel/<int:server_id>/', views.panel, name='panel'),
    path('add_product/', views.add_product, name='add_product'),
    path('add_operator/<operator_type>', views.add_operator, name='add_operator'),
    path('save_settings2/', views.save_settings2, name='save_settings2'),
    path('remove_product/', views.remove_product, name='remove_product'),
    path('generate_voucher/', views.generate_voucher, name='generate_voucher'),
    path('customize_website/', views.customize_website, name='customize_website'),
    path('remove_payment_operator/', views.remove_payment_operator, name='remove_payment_operator'),
    path('shop/<int:server_id>/', views.shop, name='shop'),
    path('buy_sms/', views.buy_sms, name='buy_sms'),
    path('buy_other/', views.buy_other, name='buy_other'),
    path('lvlup_check', views.lvlup_check, name='lvlup_check'),
    path('use_voucher/', views.use_voucher, name='use_voucher'),
    path('success/', views.success_page, name='success_page'),
    path('faq/', views.faq, name='faq'),
    path('check_rcon_status/', views.check_rcon_status, name='check_rcon_status')
]
