import json

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.conf import settings
from lvluppayments import Payments

from shop.utils.oauth2 import Oauth
from shop.utils.functions import authorize_panel, send_commands, check_rcon_connection, login_required, generate_random_chars
from .models import Server, PaymentOperator, Product, Purchase, Voucher

import requests

if not settings.DEBUG:
    from shop.utils.functions import actualize_servers_data
    actualize_servers_data()


def index(request):
    if 'username' and 'user_id' in request.session:
        data = Server.objects.filter(owner_id=request.session['user_id'])
        context = {'data': data}
        return render(request, "index.html", context)
    return render(request, "index.html")


def handler404(request, exception):
    return render(request, '404.html', status=404)


def login(request):
    if 'username' not in request.session:
        return redirect(Oauth.discord_login_url)
    del request.session['username']
    del request.session['user_id']
    return redirect(Oauth.discord_login_url)


def logout(request):
    if 'username' in request.session:
        del request.session['username']
        del request.session['user_id']
        return redirect('/')
    messages.add_message(request, messages.ERROR, 'Nie jesteś zalogowany.')
    return redirect('/')


def callback(request):
    if 'username' not in request.session:
        try:
            code = request.GET.get("code")
            access_token = Oauth.get_access_token(code)
            user_json = Oauth.get_user_json(access_token)
            username = user_json.get("username")
            user_id = user_json.get("id")
            request.session['username'] = username
            request.session['user_id'] = user_id
            return redirect('/')
        except:
            return redirect('/')
    messages.add_message(request, messages.ERROR, 'Jesteś już zalogowany.')
    return redirect('/')


@csrf_exempt
@login_required
def add_server(request):
    server_name = request.POST.get("server_name")
    server_ip = request.POST.get("server_ip")
    rcon_password = request.POST.get("rcon_password")
    rcon_port = request.POST.get("rcon_port")
    if not server_name or not server_ip or not rcon_password or not rcon_port:
        return JsonResponse({'message': 'Uzupełnij informacje o serwerze.'}, status=411)

    get_server_data = requests.get('https://api.mcsrvstat.us/2/' + server_ip).json()
    status = get_server_data["online"]
    if not status:
        return JsonResponse({'message': 'Serwer jest wyłączony.'}, status=400)
    if not check_rcon_connection(server_ip, rcon_password, rcon_port):
        return JsonResponse({'message': 'Wystąpił błąd podczas łączenia się do rcon.'}, status=400)

    i = Server(
        server_name=server_name,
        server_ip=server_ip,
        rcon_password=rcon_password,
        rcon_port=rcon_port,
        owner_id=request.session['user_id'],
        server_version=get_server_data["version"],
        server_status=True,
        server_players=str(get_server_data["players"]["online"]) + '/' + str(
            get_server_data["players"]["max"])
    )
    i.save()
    return JsonResponse({'message': 'Dodano serwer, możesz teraz odświeżyć stronę.'})


def panel(request, server_id):
    if authorize_panel(request, server_id) is True:
        counted_sells = {}
        exclude = []
        counted_products = Product.objects.filter(server__id=server_id).count()
        purchases_count = Purchase.objects.filter(product__server__id=server_id, status=1).count()
        purchases = Purchase.objects.filter(product__server__id=server_id)
        server = Server.objects.get(id=server_id)
        products = Product.objects.filter(server__id=server_id)
        vouchers = Voucher.objects.filter(product__server__id=server_id)
        payment_operators = PaymentOperator.objects.filter(server__id=server_id)
        for po in payment_operators:
            if po.operator_type == 'lvlup_sms' or po.operator_type == 'lvlup_other' or po.operator_type == 'microsms_sms':
                exclude.append(po.operator_type)
        for product in products:
            count = Purchase.objects.filter(product_id=product.id, status=1).count()
            counted_sells.update({str(product.id): count})
        context = {
            'server_id': server_id,  # Wiem, że rak, do zmiany xD
            'server_name': server.server_name,
            'server_ip': server.server_ip,
            'counted_products': counted_products,
            'purchases_count': purchases_count,
            'purchases': purchases,
            'products': products,
            'counted_sells': counted_sells,
            'vouchers': vouchers,
            'server_logo': server.logo,
            'own_css': server.own_css,
            'rcon_port': server.rcon_port,
            'payment_operators': payment_operators,
            'assigned_operators': exclude
        }
        return render(request, 'panel.html', context=context)
    else:
        return authorize_panel(request, server_id)


@csrf_exempt
@login_required
def add_product(request):
    server_id = request.POST.get("server_id")
    product_name = request.POST.get("product_name")
    product_description = request.POST.get("product_description")
    product_price = request.POST.get("product_price")
    product_sms_price = request.POST.get("product_sms_price")
    product_commands = request.POST.get("product_commands")
    product_image = request.POST.get("product_image")
    if not product_name or not product_description or not product_price or not product_sms_price or not product_commands:
        return JsonResponse({'message': 'Uzupełnij informacje o produkcie.'}, status=411)
    if not request.POST.get('server_id') and not request.POST.get('edit_mode'):
        return JsonResponse({'message': 'Uzupełnij informacje o produkcie.'}, status=411)

    if server_id:
        check_payment_type = PaymentOperator.objects.filter(server__owner_id=request.session['user_id'], server__id=server_id)
        if not check_payment_type.exists():
            return JsonResponse({'message': 'Aby dodać produkt wybierz operatora płatności.'}, status=411)

    product_price = float(product_commands)
    product_price = float(format(product_price, '.2f'))
    if not product_price > 0.99:
        return JsonResponse({'message': 'Minimalna cena wynosi 1 PLN.'}, status=401)
    elif product_price > 999.99:
        return JsonResponse({'message': 'Maksymalna cena wynosi 999.99 PLN.'}, status=401)

    if request.POST.get('edit_mode'):
        Product.objects.select_for_update().filter(id=request.POST.get("product_id")).update(
            product_name=product_name,
            product_description=product_description,
            price=product_price,
            sms_number=product_sms_price,
            product_commands=product_commands,
            product_image=product_image)
        return JsonResponse({'message': 'Zapisano zmiany.'}, status=200)
    else:
        p = Product(
            product_name=product_name,
            product_description=product_description,
            server=Server.objects.get(id=server_id),
            price=product_price,
            sms_number=product_sms_price,
            product_commands=product_commands,
            product_image=product_image)
        p.save()
        return JsonResponse({'message': 'Dodano produkt.'}, status=200)


@csrf_exempt
@login_required
def add_operator(request, operator_type):
    if operator_type not in ['lvlup_sms', 'lvlup_other', 'microsms_sms']:
        return JsonResponse({'message': 'Taki operator nie został znaleziony.'}, status=404)

    operator_name = request.POST.get("operator_name")
    if not operator_name:
        return JsonResponse({'message': 'Uzupełnij informacje o operatorze.'}, status=411)

    client_id = request.POST.get("client_id")
    server_id = request.POST.get("server_id")
    api_key = request.POST.get("api_key")
    service_id = request.POST.get("service_id")
    sms_content = request.POST.get("sms_content")
    operator = PaymentOperator.objects.filter(operator_type=operator_type, server__id=server_id)
    if operator.exists():
        return JsonResponse({'message': 'Dodałeś już takiego operatora.'}, status=409)
    if operator_type == 'lvlup_sms' and not client_id:
        return JsonResponse({'message': 'Uzupełnij informacje o operatorze.'}, status=411)
    elif operator_type == 'lvlup_other' and not api_key:
        return JsonResponse({'message': 'Uzupełnij informacje o operatorze.'}, status=411)
    elif operator_type == 'microsms_sms':
        if not client_id or not service_id or not sms_content:
            return JsonResponse({'message': 'Uzupełnij informacje o operatorze.'}, status=411)

    authorize_user = Server.objects.filter(id=server_id).values('owner_id')
    if authorize_user and str(authorize_user[0]['owner_id']) == request.session['user_id']:
        if operator_type == 'lvlup_sms':
            new_operator = PaymentOperator(
                operator_type=operator_type,
                operator_name=operator_name,
                client_id=client_id,
                server=Server.objects.get(id=server_id)
            )
            new_operator.save()
        elif operator_type == 'lvlup_other':
            new_operator = PaymentOperator(
                operator_type=operator_type,
                operator_name=operator_name,
                api_key=api_key,
                server=Server.objects.get(id=server_id)
            )
            new_operator.save()
        elif operator_type == 'microsms_sms':
            new_operator = PaymentOperator(
                operator_type=operator_type,
                operator_name=operator_name,
                client_id=client_id,
                service_id=service_id,
                sms_content=sms_content,
                server=Server.objects.get(id=server_id)
            )
            new_operator.save()
        messages.add_message(request, messages.SUCCESS, 'Dodano nowego operatora płatności.')
        return JsonResponse({'message': 'Zapisano ustawienia'}, status=200)
    return JsonResponse({'message': 'Otóż nie tym razem ( ͡° ͜ʖ ͡°)'}, status=401)


def shop(request, server_id):
    try:
        check_server_exists = Server.objects.get(id=server_id)
    except:
        return render(request, '404.html')
    products = Product.objects.filter(server__id=server_id)
    purchases = Purchase.objects.filter(product__server__id=server_id, status=1).order_by('-id')[0:5]
    context = {
        'server': check_server_exists,
        'products': products,
        'purchases': purchases
    }
    return render(request, 'shop.html', context=context)


@csrf_exempt
def buy_sms(request):
    player_nick = request.POST.get('player_nick')
    sms_code = request.POST.get('sms_code')
    sms_number = request.POST.get('sms_number')
    product_id = request.POST.get('product_id')
    if not player_nick or not sms_code or not product_id or not sms_number:
        return JsonResponse({'message': 'Uzupełnij dane.'}, status=411)

    product = Product.objects.filter(id=product_id,sms_number=sms_number).values('server__client_id',
                                                                                 'server__server_ip',
                                                                                 'server__rcon_password',
                                                                                 'product_commands',
                                                                                 'server__server_status',
                                                                                 'server__rcon_port',
                                                                                 'server__microsms_service_id')
    if not product.exists():
        return JsonResponse({'message': 'Otóż nie tym razem ( ͡° ͜ʖ ͡°).'}, status=401)
    if product[0]['server__server_status'] == 0:
        return JsonResponse({'message': 'Serwer jest aktualnie wyłączony, zachowaj kod i wykorzystaj go, gdy serwer będzie włączony.'}, status=411)

    client_id = product[0]['server__client_id']
    if request.POST.get("payment_type") == "1":
        url = f"https://lvlup.pro/api/checksms?id={client_id}&code={sms_code}&number={sms_number}&desc=[IVshop] Zarobek z itemshopu"
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
            lvlup_id="sms",
            buyer=player_nick,
            product=Product.objects.get(id=product_id),
            status=1,
        )
        p.save()
        return JsonResponse({'message': 'Zakupiono produkt.'}, status=200)

    elif request.POST.get("payment_type") == "2":
        service_id = product[0]['server__microsms_service_id']
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
                lvlup_id="microsms",
                buyer=player_nick,
                product=Product.objects.get(id=product_id),
                status=1,
            )
            p.save()
            return JsonResponse({'message': 'Zakupiono produkt.'}, status=200)


@csrf_exempt
def buy_other(request):
    product_id = request.POST.get('product_id')
    player_nick = request.POST.get('player_nick')
    if not product_id or not player_nick:
        return JsonResponse({'message': 'Uzupełnij dane.'}, status=411)

    api_key = Product.objects.filter(id=product_id).values('server__api_key', 'price', 'server__server_status')
    if api_key[0]['server__server_status'] == 0:
        return JsonResponse({'message': 'Serwer jest aktualnie wyłączony.'}, status=411)

    price = api_key[0]['price']
    if settings.DEBUG:
        payment = Payments(api_key[0]['server__api_key'], 'sandbox')
    else:
        payment = Payments(api_key[0]['server__api_key'], 'production')
    domain = 'https://'+str(request.META['HTTP_HOST'])
    success_page2 = str(domain)+"/success"
    lvlup_check_page = str(domain)+"/lvlup_check"
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
def lvlup_check(request):
    data = json.loads(request.body)
    paymentId = data['paymentId']
    status = data['status']
    purchase = Purchase.objects.filter(lvlup_id=paymentId).values('id', 'product__product_commands', 'buyer',
                                                                       'product__server__server_ip',
                                                                       'product__server__rcon_password',
                                                                       'product__product_commands',
                                                                       'product__server__api_key', 'product__server__rcon_port')
    if settings.DEBUG:
        payment = Payments(str(purchase[0]['product__server__api_key']), 'sandbox')
    else:
        payment = Payments(str(purchase[0]['product__server__api_key']), 'production')

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
        return JsonResponse({'message': 'Udało się.'}, status=200)
    return JsonResponse({'message': 'Otóż nie tym razem ( ͡° ͜ʖ ͡°).'}, status=401)


@csrf_exempt
@login_required
def save_settings2(request):
    server_id = request.POST.get("server_id")
    server_name = request.POST.get("server_name")
    server_ip = request.POST.get("server_ip")
    server_rcon_password = request.POST.get("rcon_password")
    server_rcon_port = request.POST.get("rcon_port")
    if not server_id or not server_name or not server_ip or not server_rcon_password or not server_rcon_port:
        return JsonResponse({'message': 'Uzupełnij informacje o serwerze.'}, status=411)

    server = Server.objects.filter(id=server_id).values('owner_id')

    if not server.exists() or not str(server[0]['owner_id']) == request.session['user_id']:
        return JsonResponse({'message': 'Otóż nie tym razem ( ͡° ͜ʖ ͡°)'}, status=401)
    if not check_rcon_connection(server_ip, server_rcon_password, server_rcon_port):
        return JsonResponse({'message': 'Wystąpił błąd podczas łączenia się do rcon.'}, status=400)

    server.update(
        server_name=server_name,
        server_ip=server_ip,
        rcon_password=server_rcon_password,
        rcon_port=server_rcon_port)
    return JsonResponse({'message': 'Zapisano ustawienia'}, status=200)


@csrf_exempt
@login_required
def remove_product(request):
    product_id = request.POST.get('product_id')
    product_to_delete = Product.objects.filter(id=product_id, server__owner_id=request.session['user_id'])
    if not product_to_delete.exists():
        return JsonResponse({'message': 'Otóż nie tym razem ( ͡° ͜ʖ ͡°)'}, status=401)

    product_to_delete.delete()
    return JsonResponse({'message': 'Produkt został usunięty.'}, status=200)


@csrf_exempt
@login_required
def product_info(request):
    product_id = request.GET.get('product_id')
    product = Product.objects.filter(id=product_id, server__owner_id=request.session['user_id'])
    if not product.exists():
        return JsonResponse({'message': 'Otóż nie tym razem ( ͡° ͜ʖ ͡°)'}, status=401)

    return JsonResponse({
        'product_name': product[0].product_name,
        'product_description': product[0].product_description,
        'price': format(float(product[0].price), '.2f'),
        'sms_number': product[0].sms_number,
        'commands': product[0].product_commands,
        'product_image': product[0].product_image
    })


@csrf_exempt
@login_required
def generate_voucher(request):
    product_id = request.POST.get('product_id')
    product = Product.objects.filter(id=product_id, server__owner_id=request.session['user_id'])
    if not product.exists():
        return JsonResponse({'message': 'Otóż nie tym razem ( ͡° ͜ʖ ͡°)'}, status=401)

    code = generate_random_chars(6)
    v = Voucher(
        product=Product.objects.get(id=product_id),
        code=code,
        status=0
    )
    v.save()
    return JsonResponse({'message': 'Voucher został wygenerowany. Znajdziesz go w liście voucherów.'}, status=200)


@csrf_exempt
def use_voucher(request):
    player_nick = request.POST.get('player_nick')
    voucher_code = request.POST.get('voucher_code')
    server_id = request.POST.get('server_id')
    if not player_nick or not voucher_code or not server_id:
        return JsonResponse({'message': 'Uzupełnij dane.'}, status=411)

    voucher = Voucher.objects.filter(code=voucher_code, status=0, product__server_id=server_id).values('product__server__server_ip',
                                                                   'product__server__rcon_password',
                                                                   'product__product_commands', 'product__server__rcon_port')
    if not voucher.exists():
        return JsonResponse({'message': 'Niepoprawny kod'}, status=401)

    server_ip = voucher[0]['product__server__server_ip']
    rcon_password = voucher[0]['product__server__rcon_password']
    commands = voucher[0]['product__product_commands'].split(';')
    rcon_port = voucher[0]['product__server__rcon_port']
    try:
        send_commands(server_ip, rcon_password, commands, player_nick, rcon_port)
    except:
        return JsonResponse({'message': 'Wystąpił błąd podczas łączenia się do rcon.'}, status=401)

    voucher.update(status=1, player=player_nick)
    return JsonResponse({'message': 'Voucher został wykorzystany.'}, status=200)



def success_page(request):
    return render(request, 'success.html')


@csrf_exempt
@login_required
def customize_website(request):
    server_id = request.POST.get("server_id")
    Server.objects.select_for_update().filter(id=server_id, owner_id=request.session['user_id']).update(
        logo=request.POST.get("server_logo"),
        own_css=request.POST.get("own_css"),
        shop_style=request.POST.get("shop_style"))
    return JsonResponse({'message': 'Zapisano.'}, status=200)


@csrf_exempt
@login_required
def remove_payment_operator(request):
    operator_id = request.POST.get("operator_id")
    operator = PaymentOperator.objects.filter(id=operator_id, server__owner_id=request.session['user_id'])
    if not operator.exists():
        return JsonResponse({'message': 'Nie znaleziono takiego operatora.'}, status=404)
    operator.delete()
    messages.add_message(request, messages.SUCCESS, 'Operator został usunięty.')
    return JsonResponse({'message': 'Operator został usunięty.'}, status=200)
