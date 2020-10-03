import threading
from shop.models import Server
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import redirect
from mcrcon import MCRcon
import requests
import random
import string


# Sprawdza, czy użytkownik jest zalogowany i posiada dostęp do zarządzania serwerem
def login_required(function):
    def wrapper(request, *args, **kw):
        if not 'username' in request.session or not 'user_id' in request.session:
            if request.method == 'GET':
                messages.add_message(request, messages.ERROR, 'Nie jesteś zalogowany.')
                return redirect('/')
            else:
                return JsonResponse({'message': 'Wystąpił błąd z sesją użytkownika.'}, status=401)

        else:
            try:
                server_id = kw['server_id']
            except KeyError as e:
                server_id = request.POST.get('server_id')

            user_id = request.session['user_id']
            owner_id = Server.objects.filter(id=server_id).values('owner_id')

            if not owner_id:
                messages.add_message(request, messages.ERROR, 'Taki serwer nie istnieje.')
                return redirect('/')

            admins = Server.get_admins(server_id)
            if int(user_id) == owner_id[0]['owner_id'] or user_id in admins:
                return function(request, *args, **kw)

            if request.method == 'GET':
                messages.add_message(request, messages.ERROR, 'Nie posiadasz dostępu do tego serwera.')
                return redirect('/')
            else:
                return JsonResponse({'message': 'Nie posiadasz dostępu do tego serwera.'}, status=401)
    return wrapper


def send_webhook_discord(webhook_url, buyer, product_name):
    json_payload = {
        "embeds": [
            {
                "title": "Zakup produktu",
                "image": {
                    "url": f"https://minotar.net/avatar/{buyer}/50"
                },
                "color": 3066993,
                "description": f"Gracz **{buyer}** zakupił **{product_name}**. Dziękujemy! :heart:"
            }],
    }

    r = requests.post(webhook_url, json=json_payload)


def send_commands(server_ip, rcon_password, commands, buyer, rcon_port):
    server_ip = str(server_ip).split(':')[0]
    mcr = MCRcon(server_ip, rcon_password, int(rcon_port))
    mcr.connect()
    for command in commands:
        mcr.command(command.replace("{PLAYER}", buyer))
    mcr.disconnect()


def check_rcon_connection(server_ip, rcon_password, rcon_port):
    try:
        new_server_ip = str(server_ip).split(':')[0]
        print(new_server_ip)
        mcr = MCRcon(new_server_ip, rcon_password, int(rcon_port))
        mcr.connect()
        mcr.disconnect()
        return True
    except Exception as e:
        print(e)
        return False


def generate_random_chars(length):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))


def actualize_servers_data():
    threading.Timer(60 * 6, actualize_servers_data).start()  # Funkcja wywoływana co 6 minut
    for server in Server.objects.all():
        get_server_data = requests.get('https://api.mcsrvstat.us/2/' + server.server_ip).json()
        status = get_server_data["online"]
        if status:
            version = get_server_data["version"]
            players = str(get_server_data["players"]["online"]) + '/' + str(get_server_data["players"]["max"])
            Server.objects.filter(id=server.id).update(server_status=status, server_version=version,
                                                       server_players=players)
        else:
            Server.objects.filter(id=server.id).update(server_status=status)
