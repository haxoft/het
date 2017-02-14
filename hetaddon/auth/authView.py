from django.http import *
from django.views.decorators.csrf import csrf_exempt
import json

from hetaddon.auth.authManager import AuthManager


# called after the addon is installed on Atlassian
@csrf_exempt
def addon_installed(request):

    data = json.loads(request.body.decode('utf-8'))
    print("The Addon has been installed! Payload:" + str(data))
    AuthManager.register_tenant(data)  # stores the shared secret in DB
    return HttpResponse("OK", status=200)


@csrf_exempt
def addon_uninstalled(request):

    return HttpResponse("OK", status=200)