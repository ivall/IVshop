from django.urls import path
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
    path('use_voucher/', views.use_voucher, name='use_voucher'),
    path('success/', views.success_page, name='success_page'),
    path('faq/', views.faq, name='faq'),
    path('check_rcon_status/', views.check_rcon_status, name='check_rcon_status'),
    path('add_link/', views.add_link, name='add_link'),
    path('remove_link/', views.remove_link, name='remove_link')
]
