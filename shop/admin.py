from django.contrib import admin
from .models import Server, Product, Purchase, Voucher, PaymentOperator

admin.site.register(Server)
admin.site.register(PaymentOperator)
admin.site.register(Product)
admin.site.register(Purchase)
admin.site.register(Voucher)

