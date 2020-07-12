from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from lvluppayments import Payments

from mcrcon import MCRcon

from shop.utils.oauth2 import Oauth
from shop.utils.functions import authorize_panel
from .models import Server, Product

import requests
import re

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
                try:
                    mcr = MCRcon(request.POST.get("server_ip"), request.POST.get("rcon_password"))
                    mcr.connect()
                    mcr.disconnect()
                except:
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
        counted_products = Product.objects.filter(server__id=server_id).count()
        server = Server.objects.get(id=server_id)
        context = {
            'server_id': server_id,
            'server_name': server.server_name,
            'counted_products': counted_products
        }
        return render(request, 'panel.html', context=context)
    else:
        return authorize_panel(request, server_id)


@csrf_exempt
def add_product(request):
    if 'username' in request.session and 'user_id' in request.session and request.method == 'POST':
        if not request.POST.get("server_id") or not request.POST.get("product_name") or not request.POST.get("product_description") or not request.POST.get("product_price") or not request.POST.get("product_sms_price") or not request.POST.get("product_commands"):
            return JsonResponse({'message': 'Uzupełnij informacje o produkcie.'}, status=411)
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
    check_server_exists = Server.objects.get(id=server_id)
    if check_server_exists:
        products = Product.objects.filter(server__id=server_id)
        context = {
            'server': check_server_exists,
            'products': products
        }
        return render(request, 'shop.html', context=context)
    return redirect('/')


@csrf_exempt
def buy_sms(request):
    if not request.POST.get('player_nick') or not request.POST.get('sms_code') or request.POST.get('sms_code') == 'TEST' or not request.method == "POST":
        return JsonResponse({'message': 'Uzupełnij dane.'}, status=411)
    check_product = Product.objects.filter(id=request.POST.get("product_id"), sms_number=request.POST.get("sms_number")).values('server__client_id', 'server__server_ip', 'server__rcon_password', 'product_commands')
    if not check_product:
        return JsonResponse({'message': 'Otóż nie tym razem ( ͡° ͜ʖ ͡°).'}, status=401)
    number = request.POST.get("sms_number")
    code = request.POST.get('sms_code')
    client_id = check_product[0]['server__client_id']
    url = f"https://lvlup.pro/api/checksms?id={client_id}&code={code}&number={number}&desc=[IVshop] Zarobek z itemshopu"
    r = requests.get(url).json()
    if r['valid']:
        server_ip = check_product[0]['server__server_ip']
        rcon_password = check_product[0]['server__rcon_password']
        commands = check_product[0]['product_commands'].split(';')
        mcr = MCRcon(server_ip, rcon_password)
        mcr.connect()
        for command in commands:
            mcr.command(command.replace("{PLAYER}", request.POST.get('player_nick')))
        mcr.disconnect()
        return JsonResponse({'message': 'Zakupiono produkt.'}, status=200)
    return JsonResponse({'message': 'Niepoprawny kod SMS.'}, status=401)
