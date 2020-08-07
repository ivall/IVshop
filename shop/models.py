from django.db import models
from django.utils import timezone


class Server(models.Model):
    server_name = models.CharField(max_length=16)
    server_ip = models.CharField(max_length=32)
    rcon_password = models.CharField(max_length=100)
    rcon_port = models.IntegerField()
    owner_id = models.IntegerField()
    server_version = models.CharField(max_length=50)
    server_status = models.BooleanField(default=True)
    server_players = models.CharField(max_length=10)
    logo = models.URLField(blank=True)
    own_css = models.URLField(blank=True)
    shop_style = models.CharField(max_length=5, default="light")


"""
Lista operatorów płatności:
- lvlup_sms
- lvlup_other
_ microsms_sms
"""


class PaymentOperator(models.Model):
    operator_name = models.CharField(max_length=20)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    operator_type = models.CharField(max_length=20)  # Na przykład lvlup_sms albo microsms_sms
    """
    Opcjonalne, na przykład dla microsms_sms wymagane jest 
    client_id, service_id, sms_content, a dla lvlup_sms tylko client_id
    """
    client_id = models.IntegerField(blank=True, null=True)
    api_key = models.CharField(max_length=64, blank=True, null=True)
    service_id = models.IntegerField(blank=True, null=True)
    sms_content = models.CharField(max_length=16, blank=True, null=True)


class Product(models.Model):
    product_name = models.CharField(max_length=100)
    product_description = models.CharField(max_length=200)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    price = models.CharField(max_length=10)
    sms_number = models.IntegerField()
    product_commands = models.CharField(max_length=2000)
    product_image = models.URLField(blank=True, default="")


class Purchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    buyer = models.CharField(max_length=32)
    lvlup_id = models.CharField(max_length=16)
    status = models.IntegerField()
    date = models.DateTimeField(default=timezone.localtime(timezone.now()), blank=True)


class Voucher(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    code = models.CharField(max_length=8)
    player = models.CharField(max_length=16)
    status = models.BooleanField()
