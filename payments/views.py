import json
import requests
import re

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from lvluppayments.payments import Payments

from shop.utils.functions import send_commands, send_webhook_discord, validate_player_nick
from shop.models import PaymentOperator, Product, Purchase


@csrf_exempt
def buy_lvlup_sms(request):
    player_nick = request.POST.get('player_nick')
    sms_code = request.POST.get('sms_code')
    sms_number = request.POST.get('sms_number')
    product_id = request.POST.get('product_id')
    if not player_nick or not sms_code or not product_id or not sms_number:
        return JsonResponse({'message': 'Uzupełnij dane.'}, status=411)

    if not validate_player_nick(player_nick):
        return JsonResponse({'message': 'Niepoprawny format nicku.'}, status=406)

    product = Product.objects.filter(id=product_id, lvlup_sms_number=sms_number).values('server__server_ip',
                                                                                  'server__rcon_password',
                                                                                  'product_commands',
                                                                                  'server__server_status', 'product_name',
                                                                                  'server__rcon_port', 'server__id', 'server__discord_webhook')
    server_id = product[0]['server__id']

    payment_operator = PaymentOperator.objects.filter(server__id=server_id, operator_type='lvlup_sms').values('client_id')
    
    if not product.exists() or not payment_operator.exists():
        return JsonResponse({'message': 'Otóż nie tym razem ( ͡° ͜ʖ ͡°).'}, status=401)
    if product[0]['server__server_status'] == 0:
        return JsonResponse(
            {'message': 'Serwer jest aktualnie wyłączony, zachowaj kod i wykorzystaj go, gdy serwer będzie włączony.'},
            status=411
            )

    client_id = payment_operator[0]['client_id']

    url = f"https://lvlup.pro/api/checksms?id={client_id}&code={sms_code}&number={sms_number}&desc=[IVshop] Zarobek z itemshopu ({player_nick})"
    r = requests.get(url).json()
    if not r['valid']:
        return JsonResponse({'message': 'Niepoprawny kod SMS.'}, status=401)

    server_ip = product[0]['server__server_ip']
    rcon_password = product[0]['server__rcon_password']
    commands = product[0]['product_commands'].split(';')
    rcon_port = product[0]['server__rcon_port']
    try:
        send_commands(server_ip, rcon_password, commands, player_nick, rcon_port)
    except:
        return JsonResponse({'message': 'Wystąpił błąd podczas łączenia się do rcon.'}, status=401)

    p = Purchase(
        lvlup_id="lvlup_sms",
        buyer=player_nick,
        product=Product.objects.get(id=product_id),
        status=1,
    )
    p.save()
    if product[0]['server__discord_webhook']:
        send_webhook_discord(product[0]['server__discord_webhook'], player_nick, product[0]['product_name'])
    return JsonResponse({'message': 'Zakupiono produkt.'}, status=200)


@csrf_exempt
def buy_microsms_sms(request):
    player_nick = request.POST.get('player_nick')
    sms_code = request.POST.get('sms_code')
    sms_number = request.POST.get('sms_number')
    product_id = request.POST.get('product_id')
    if not player_nick or not sms_code or not product_id or not sms_number:
        return JsonResponse({'message': 'Uzupełnij dane.'}, status=411)

    if not validate_player_nick(player_nick):
        return JsonResponse({'message': 'Niepoprawny format nicku.'}, status=406)

    product = Product.objects.filter(id=product_id, microsms_sms_number=sms_number).values('server__server_ip',
                                                                                  'server__rcon_password',
                                                                                  'product_commands',
                                                                                  'server__server_status', 'product_name',
                                                                                  'server__rcon_port', 'server__id', 'server__discord_webhook')

    payment_operator = PaymentOperator.objects.filter(server__id=product[0]['server__id'], operator_type='microsms_sms').values('client_id', 'sms_content', 'service_id')

    if not product.exists() or not payment_operator.exists():
        return JsonResponse({'message': 'Otóż nie tym razem ( ͡° ͜ʖ ͡°).'}, status=401)
    if product[0]['server__server_status'] == 0:
        return JsonResponse(
            {'message': 'Serwer jest aktualnie wyłączony, zachowaj kod i wykorzystaj go, gdy serwer będzie włączony.'},
            status=411
            )

    client_id = payment_operator[0]['client_id']
    service_id = payment_operator[0]['service_id']

    pattern = re.compile("^[A-Za-z0-9]{8}$")
    if not pattern.match(sms_code):
        return JsonResponse({'message': 'Niepoprawny format kodu.'}, status=406)

    url = f'https://microsms.pl/api/check_multi.php?userid={client_id}&code={sms_code}&serviceid={service_id}'
    r = requests.get(url)
    payment_status = r.text.strip()
    if payment_status == "E,2":
        return JsonResponse({'message': 'Brak partnera lub usługi.'}, status=401)
    elif payment_status == "E,3":
        return JsonResponse({'message': 'Niepoprawny numer SMS.'}, status=401)
    elif payment_status == "E,2":
        return JsonResponse({'message': 'Niepoprawny format kodu.'}, status=401)
    elif payment_status[0] == "0":
        return JsonResponse({'message': 'Niepoprawny kod SMS.'}, status=401)
    elif payment_status[0] == "1":
        server_ip = product[0]['server__server_ip']
        rcon_password = product[0]['server__rcon_password']
        commands = product[0]['product_commands'].split(';')
        rcon_port = product[0]['server__rcon_port']
        try:
            send_commands(server_ip, rcon_password, commands, player_nick, rcon_port)
        except:
            return JsonResponse({'message': 'Wystąpił błąd podczas łączenia się do rcon.'}, status=401)

        p = Purchase(
            lvlup_id="microsms_sms",
            buyer=player_nick,
            product=Product.objects.get(id=product_id),
            status=1,
        )
        p.save()
        if product[0]['server__discord_webhook']:
            send_webhook_discord(product[0]['server__discord_webhook'], player_nick, product[0]['product_name'])
        return JsonResponse({'message': 'Zakupiono produkt.'}, status=200)


@csrf_exempt
def buy_lvlup_other(request):
    product_id = request.POST.get('product_id')
    player_nick = request.POST.get('player_nick')
    if not product_id or not player_nick:
        return JsonResponse({'message': 'Uzupełnij dane.'}, status=411)

    if not validate_player_nick(player_nick):
        return JsonResponse({'message': 'Niepoprawny format nicku.'}, status=406)

    product = Product.objects.filter(id=product_id).values('lvlup_other_price', 'server__server_status', 'server_id')
    payment_operator = PaymentOperator.objects.filter(server_id=product[0]['server_id'], operator_type='lvlup_other').values('api_key')

    if product[0]['server__server_status'] == 0:
        return JsonResponse({'message': 'Serwer jest aktualnie wyłączony.'}, status=411)

    price = product[0]['lvlup_other_price']
    if settings.DEBUG:
        payment = Payments(payment_operator[0]['api_key'], 'sandbox')
    else:
        payment = Payments(payment_operator[0]['api_key'], 'production')

    domain = 'https://' + str(request.META['HTTP_HOST'])
    success_page2 = str(domain) + "/success"
    lvlup_check_page = str(domain) + "/payments/webhook/lvlup_other"
    link = payment.create_payment(format(float(price), '.2f'), success_page2, lvlup_check_page)

    try:
        url = link['url']
        payment_id = link['id']
    except:
        return JsonResponse({'message': 'Wystąpił błąd, prawdopodobnie niepoprawny klucz api.'}, status=401)
    p = Purchase(
        lvlup_id=payment_id,
        buyer=player_nick,
        product=Product.objects.get(id=product_id),
        status=0,
    )
    p.save()
    return JsonResponse({'message': url}, status=200)


@csrf_exempt
def webhook_lvlup_other(request):
    data = json.loads(request.body)
    paymentId = data['paymentId']
    status = data['status']
    purchase = Purchase.objects.filter(lvlup_id=paymentId).values('id', 'product__product_commands', 'buyer',
                                                                  'product__server__server_ip',
                                                                  'product__server__rcon_password',
                                                                  'product__product_commands',
                                                                  'product__server__rcon_port', 'product__server_id', 'product__product_name',
                                                                  'product__server__discord_webhook')
    payment_operator = PaymentOperator.objects.filter(server_id=purchase[0]['product__server_id'], operator_type='lvlup_other').values('api_key')

    if settings.DEBUG:
        payment = Payments(str(payment_operator[0]['api_key']), 'sandbox')
    else:
        payment = Payments(str(payment_operator[0]['api_key']), 'production')

    if purchase.exists() and status == 'CONFIRMED' and payment.is_paid(str(paymentId)):
        server_ip = purchase[0]['product__server__server_ip']
        rcon_password = purchase[0]['product__server__rcon_password']
        commands = purchase[0]['product__product_commands'].split(';')
        rcon_port = purchase[0]['product__server__rcon_port']
        try:
            send_commands(server_ip, rcon_password, commands, purchase[0]['buyer'], rcon_port)
        except:
            return JsonResponse({'message': 'Wystąpił błąd podczas łączenia się do rcon.'}, status=401)
        purchase.update(status=1)
        if purchase[0]['product__server__discord_webhook']:
            send_webhook_discord(purchase[0]['product__server__discord_webhook'], purchase[0]['buyer'], purchase[0]['product__product_name'])
        return JsonResponse({'message': 'Udało się.'}, status=200)
    return JsonResponse({'message': 'Otóż nie tym razem ( ͡° ͜ʖ ͡°).'}, status=401)
