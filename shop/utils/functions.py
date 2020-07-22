import threading
from shop.models import Server
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import redirect
from mcrcon import MCRcon
import requests
import random
import string


def login_required(function):
    def wrapper(request, *args, **kw):
        if not 'username' in request.session or not 'user_id' in request.session:
            if request.method == 'GET':
                messages.add_message(request, messages.ERROR, 'Nie jesteś zalogowany.')
                return redirect('/')
            else:
                return JsonResponse({'message': 'Wystąpił błąd z sesją użytkownika.'}, status=401)
        else:
            return function(request, *args, **kw)
    return wrapper


def send_commands(server_ip, rcon_password, commands, buyer):
    mcr = MCRcon(server_ip, rcon_password)
    mcr.connect()
    for command in commands:
        mcr.command(command.replace("{PLAYER}", buyer))
    mcr.disconnect()


def check_rcon_connection(server_ip, rcon_password):
    try:
        mcr = MCRcon(server_ip, rcon_password)
        mcr.connect()
        mcr.disconnect()
        return True
    except:
        return False


def generate_random_chars(length):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))


@login_required
def authorize_panel(request, server_id):
    check_user_is_owner = Server.objects.filter(id=server_id, owner_id=request.session['user_id'])
    if check_user_is_owner:
        return True
    else:
        messages.add_message(request, messages.ERROR, 'Taki serwer nie istnieje lub nie jesteś jego właścicielem.')
        return redirect('/')


def actualize_servers_data():
    threading.Timer(60 * 6, actualize_servers_data).start()  # called every 6 minutes
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
