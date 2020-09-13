from rest_framework import serializers
from shop.models import Server, Product, Purchase


class ServerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Server
        fields = ('id', 'server_name', 'server_version', 'server_status',
                  'server_players', 'logo', 'own_css', 'shop_style')


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ('product_name', 'product_description', 'server_id', 'product_commands',
                  'product_image', 'lvlup_other_price', 'lvlup_sms_number', 'microsms_sms_number')

