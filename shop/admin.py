from django.contrib import admin
from .models import Server, Product, Purchase, Voucher

admin.site.register(Server)
admin.site.register(Product)
admin.site.register(Purchase)
admin.site.register(Voucher)

