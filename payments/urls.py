from django.urls import path
from . import views

urlpatterns = [
    path('buy/lvlup_other/', views.buy_lvlup_other, name='buy_lvlup_other'),
    path('webhook/lvlup_other/', views.webhook_lvlup_other, name='webhook_lvlup_other'),
    path('buy/lvlup_sms/', views.buy_lvlup_sms, name='buy_lvlup_sms'),
    path('buy/microsms_sms/', views.buy_microsms_sms, name='buy_microsms_sms'),
]
