import json

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from lvluppayments import Payments

from mcrcon import MCRcon

from shop.utils.oauth2 import Oauth
from shop.utils.functions import authorize_panel, send_commands, check_rcon_connection
from .models import Server, Product, Purchase

import requests

"""
from shop.utils.functions import actualize_servers_data

actualize_servers_data()
"""


def index(request):
    if 'username' and 'user_id' in request.session:
        data = Server.objects.filter(owner_id=request.session['user_id'])
        context = {'data': data}
        return render(request, "index.html", context)
    return render(request, "index.html")


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
def add_server(request):
    if 'username' in request.session and 'user_id' in request.session and request.method == 'POST':
        if not request.POST.get("server_name") or not request.POST.get("server_ip") or not request.POST.get(
                "rcon_password"):
            return JsonResponse({'message': 'Uzupełnij informacje o serwerze.'}, status=411)
        check_server = Server.objects.filter(server_ip=request.POST.get("server_ip"))
        if not check_server:
            get_server_data = requests.get('https://api.mcsrvstat.us/2/' + request.POST.get("server_ip")).json()
            status = get_server_data["online"]
            if status:
                if not check_rcon_connection(request.POST.get("server_ip"), request.POST.get("rcon_password")):
                    return JsonResponse({'message': 'Wystąpił błąd podczas łączenia się do rcon.'}, status=400)
                i = Server(
                    server_name=request.POST.get("server_name"),
                    server_ip=request.POST.get("server_ip"),
                    rcon_password=request.POST.get("rcon_password"),
                    owner_id=request.session['user_id'],
                    server_version=get_server_data["version"],
                    server_status=True,
                    server_players=str(get_server_data["players"]["online"]) + '/' + str(
                        get_server_data["players"]["max"])
                )
                i.save()
                return JsonResponse({'message': 'Dodano serwer, możesz teraz odświeżyć stronę.'})
            return JsonResponse({'message': 'Serwer jest wyłączony.'}, status=400)
        return JsonResponse({'message': 'Serwer z takim ip jest już dodany.'}, status=409)
    return JsonResponse({'message': 'Wystąpił błąd z sesją użytkownika lub metodą.'}, status=401)


def panel(request, server_id):
    if authorize_panel(request, server_id) is True:
        counted_sells = {}
        counted_products = Product.objects.filter(server__id=server_id).count()
        purchases_count = Purchase.objects.filter(product__server__id=server_id, status=1).count()
        purchases = Purchase.objects.filter(product__server__id=server_id)
        server = Server.objects.get(id=server_id)
        products = Product.objects.filter(server__id=server_id)
        for product in products:
            count = Purchase.objects.filter(product_id=product.id, status=1).count()
            counted_sells.update({str(product.id): count})
        context = {
            'server_id': server_id,
            'server_name': server.server_name,
            'server_ip': server.server_ip,
            'counted_products': counted_products,
            'purchases_count': purchases_count,
            'purchases': purchases,
            'client_id': server.client_id,
            'products': products,
            'counted_sells': counted_sells
        }
        return render(request, 'panel.html', context=context)
    else:
        return authorize_panel(request, server_id)


@csrf_exempt
def add_product(request):
    if 'username' in request.session and 'user_id' in request.session and request.method == 'POST':
        if not request.POST.get("product_name") or not request.POST.get(
                "product_description") or not request.POST.get("product_price") or not request.POST.get(
                "product_sms_price") or not request.POST.get("product_commands"):
            return JsonResponse({'message': 'Uzupełnij informacje o produkcie.'}, status=411)
        if not request.POST.get('server_id') and not request.POST.get('edit_mode'):
            return JsonResponse({'message': 'Uzupełnij informacje o produkcie.'}, status=411)
        if request.POST.get('server_id'):
            check_payment_type = Server.objects.filter(owner_id=request.session['user_id'],
                                                       id=request.POST.get('server_id')).values('payment_type')
            if not check_payment_type:
                return JsonResponse({'message': 'Otóż nie tym razem ( ͡° ͜ʖ ͡°)'}, status=401)
            elif not check_payment_type[0]['payment_type']:
                return JsonResponse({'message': 'Aby dodać produkt wybierz operatora płatności w ustawieniach.'},
                                    status=411)
        product_price = float(request.POST.get('product_price'))
        product_price = float(format(product_price, '.2f'))
        if not product_price > 0.99:
            return JsonResponse({'message': 'Minimalna cena wynosi 1 PLN.'}, status=401)
        elif product_price > 999.99:
            return JsonResponse({'message': 'Maksymalna cena wynosi 999.99 PLN.'}, status=401)
        if request.POST.get('edit_mode'):
            Product.objects.filter(id=request.POST.get("product_id")).update(
                product_name=request.POST.get("product_name"),
                product_description=request.POST.get("product_description"),
                price=request.POST.get("product_price"),
                sms_number=request.POST.get("product_sms_price"),
                product_commands=request.POST.get("product_commands"))
            return JsonResponse({'message': 'Zapisano zmiany.'}, status=200)
        else:
            p = Product(
                product_name=request.POST.get("product_name"),
                product_description=request.POST.get("product_description"),
                server=Server.objects.get(id=request.POST.get("server_id")),
                price=product_price,
                sms_number=request.POST.get("product_sms_price"),
                product_commands=request.POST.get("product_commands"),
            )
            p.save()
            return JsonResponse({'message': 'Dodano produkt.'}, status=200)
    return JsonResponse({'message': 'Wystąpił błąd z sesją użytkownika lub metodą.'}, status=401)


@csrf_exempt
def save_settings(request):
    if 'username' in request.session and 'user_id' in request.session and request.method == 'POST':
        if not request.POST.get("server_id") or not request.POST.get("client_id") or not request.POST.get(
                "api_key") or request.POST.get("payment_type") != "1":
            return JsonResponse({'message': 'Uzupełnij informacje o serwerze.'}, status=411)
        authorize_user = Server.objects.filter(id=request.POST.get("server_id")).values('owner_id')
        if authorize_user and str(authorize_user[0]['owner_id']) == request.session['user_id']:
            Server.objects.filter(id=request.POST.get("server_id")).update(
                payment_type=request.POST.get("payment_type"),
                api_key=request.POST.get("api_key"), client_id=request.POST.get("client_id"))
            return JsonResponse({'message': 'Zapisano ustawienia'}, status=200)
        return JsonResponse({'message': 'Otóż nie tym razem ( ͡° ͜ʖ ͡°)'}, status=401)
    return JsonResponse({'message': 'Wystąpił błąd z sesją użytkownika lub metodą.'}, status=401)


def shop(request, server_id):
    try:
        check_server_exists = Server.objects.get(id=server_id)
    except:
        return render(request, '404.html')
    products = Product.objects.filter(server__id=server_id)
    context = {
        'server': check_server_exists,
        'products': products
    }
    return render(request, 'shop.html', context=context)


@csrf_exempt
def buy_sms(request):
    if not request.POST.get('player_nick') or not request.POST.get('sms_code') or not request.method == "POST":
        return JsonResponse({'message': 'Uzupełnij dane.'}, status=411)
    check_product = Product.objects.filter(id=request.POST.get("product_id"),
                                           sms_number=request.POST.get("sms_number")).values('server__client_id',
                                                                                             'server__server_ip',
                                                                                             'server__rcon_password',
                                                                                             'product_commands',
                                                                                             'server__server_status')
    if not check_product:
        return JsonResponse({'message': 'Otóż nie tym razem ( ͡° ͜ʖ ͡°).'}, status=401)
    if check_product[0]['server__server_status'] == 0:
        return JsonResponse(
            {'message': 'Serwer jest aktualnie wyłączony, zachowaj kod i wykorzystaj go, gdy serwer będzie włączony.'},
            status=411)
    number = request.POST.get("sms_number")
    code = request.POST.get('sms_code')
    client_id = check_product[0]['server__client_id']
    url = f"https://lvlup.pro/api/checksms?id={client_id}&code={code}&number={number}&desc=[IVshop] Zarobek z itemshopu"
    r = requests.get(url).json()
    if r['valid']:
        server_ip = check_product[0]['server__server_ip']
        rcon_password = check_product[0]['server__rcon_password']
        commands = check_product[0]['product_commands'].split(';')
        try:
            send_commands(server_ip, rcon_password, commands, request.POST.get('player_nick'))
        except:
            return JsonResponse({'message': 'Wystąpił błąd podczas łączenia się do rcon.'}, status=401)
        p = Purchase(
            lvlup_id="sms",
            buyer=request.POST.get("player_nick"),
            product=Product.objects.get(id=request.POST.get("product_id")),
            status=1,
        )
        p.save()
        return JsonResponse({'message': 'Zakupiono produkt.'}, status=200)
    return JsonResponse({'message': 'Niepoprawny kod SMS.'}, status=401)


@csrf_exempt
def buy_other(request):
    if not request.POST.get('product_id') or not request.POST.get('player_nick'):
        return JsonResponse({'message': 'Uzupełnij dane.'}, status=411)
    api_key = Product.objects.filter(id=request.POST.get('product_id')).values('server__api_key', 'price',
                                                                               'server__server_status')
    if api_key[0]['server__server_status'] == 0:
        return JsonResponse({'message': 'Serwer jest aktualnie wyłączony.'}, status=411)
    price = api_key[0]['price']
    payment = Payments(api_key[0]['server__api_key'], 'sandbox')
    link = payment.create_payment(format(float(price), '.2f'), '', '')
    url = link['url']
    payment_id = link['id']
    p = Purchase(
        lvlup_id=payment_id,
        buyer=request.POST.get("player_nick"),
        product=Product.objects.get(id=request.POST.get("product_id")),
        status=0,
    )
    p.save()
    return JsonResponse({'message': url}, status=200)


@csrf_exempt
def lvlup_check(request):
    data = json.loads(request.body)
    paymentId = data['paymentId']
    status = data['status']
    check_payment = Purchase.objects.filter(lvlup_id=paymentId).values('id', 'product__product_commands', 'buyer',
                                                                       'product__server__server_ip',
                                                                       'product__server__rcon_password',
                                                                       'product__product_commands')
    if check_payment and status == 'CONFIRMED':
        server_ip = check_payment[0]['product__server__server_ip']
        rcon_password = check_payment[0]['product__server__rcon_password']
        commands = check_payment[0]['product__product_commands'].split(';')
        try:
            send_commands(server_ip, rcon_password, commands, check_payment[0]['buyer'])
        except:
            return JsonResponse({'message': 'Wystąpił błąd podczas łączenia się do rcon.'}, status=401)
        Purchase.objects.filter(id=check_payment[0]['id']).update(status=1)
        return JsonResponse({'message': 'Udało się.'}, status=200)
    return JsonResponse({'message': 'Otóż nie tym razem ( ͡° ͜ʖ ͡°).'}, status=401)


@csrf_exempt
def save_settings2(request):
    if 'username' in request.session and 'user_id' in request.session and request.method == 'POST':
        if not request.POST.get("server_id") or not request.POST.get("server_name") \
                or not request.POST.get("server_ip") or not request.POST.get("rcon_password"):
            return JsonResponse({'message': 'Uzupełnij informacje o serwerze.'}, status=411)
        authorize_user = Server.objects.filter(id=request.POST.get("server_id")).values('owner_id')
        if authorize_user and str(authorize_user[0]['owner_id']) == request.session['user_id']:
            if not check_rcon_connection(request.POST.get("server_ip"), request.POST.get("rcon_password")):
                return JsonResponse({'message': 'Wystąpił błąd podczas łączenia się do rcon.'}, status=400)
            Server.objects.filter(id=request.POST.get("server_id")).update(
                server_name=request.POST.get("server_name"),
                server_ip=request.POST.get("server_ip"),
                rcon_password=request.POST.get("rcon_password"))
            return JsonResponse({'message': 'Zapisano ustawienia'}, status=200)
        return JsonResponse({'message': 'Otóż nie tym razem ( ͡° ͜ʖ ͡°)'}, status=401)
    return JsonResponse({'message': 'Wystąpił błąd z sesją użytkownika lub metodą.'}, status=401)


@csrf_exempt
def remove_product(request):
    if 'username' in request.session and 'user_id' in request.session and request.method == 'POST':
        product_id = request.POST.get('product_id')
        check_owner = Product.objects.filter(id=product_id, server__owner_id=request.session['user_id'])
        if check_owner:
            Product.objects.filter(id=product_id).delete()
            return JsonResponse({'message': 'Produkt został usunięty.'}, status=200)
        return JsonResponse({'message': 'Otóż nie tym razem ( ͡° ͜ʖ ͡°)'}, status=401)
    return JsonResponse({'message': 'Wystąpił błąd z sesją użytkownika lub metodą.'}, status=401)


@csrf_exempt
def product_info(request):
    if 'username' in request.session:
        product_id = request.GET.get('product_id')
        product = Product.objects.filter(id=product_id, server__owner_id=request.session['user_id'])
        if not product:
            return JsonResponse({'message': 'Otóż nie tym razem ( ͡° ͜ʖ ͡°)'}, status=401)
        return JsonResponse({
            'product_name': product[0].product_name,
            'product_description': product[0].product_description,
            'price': format(float(product[0].price), '.2f'),
            'sms_number': product[0].sms_number,
            'commands': product[0].product_commands
        })
    return JsonResponse({'message': 'Wystąpił błąd z sesją użytkownika.'}, status=401)
