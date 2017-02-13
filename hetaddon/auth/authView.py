from django.http import *
from django.views.decorators.csrf import csrf_exempt
import json

from hetaddon.auth.authManager import AuthManager


# called after the addon is installed on Atlassian
@csrf_exempt
def addon_installed(request):

    data = json.loads(request.body.decode('utf-8'))
    print("The Addon has been installed! Payload:" + str(data))
    auth_manager = AuthManager(data)
    print("tenant info store:" + str(auth_manager.get_tenant_info_store()))
    return HttpResponse("OK", status=200)


@csrf_exempt
def addon_uninstalled(request):
    # TODO
    return HttpResponse("OK", status=200)