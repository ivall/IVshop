from django.db import models
from django.utils import timezone


class Server(models.Model):
    server_name = models.CharField(max_length=16)
    server_ip = models.CharField(max_length=32)
    rcon_password = models.CharField(max_length=100)
    owner_id = models.IntegerField()
    server_version = models.CharField(max_length=50)
    server_status = models.BooleanField(default=True)
    server_players = models.CharField(max_length=10)
    payment_type = models.IntegerField(default=0)  # 0 - brak wyboru, 1 - lvlup v4
    api_key = models.CharField(max_length=126)
    client_id = models.CharField(max_length=126)
    logo = models.URLField()
    own_css = models.URLField()


class Product(models.Model):
    product_name = models.CharField(max_length=100)
    product_description = models.CharField(max_length=200)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    price = models.CharField(max_length=10)
    sms_number = models.IntegerField()
    product_commands = models.CharField(max_length=2000)


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
