from django.http import *
from hetaddon.models.data import *


def get_user_from_session(request):

    if 'user' not in request.session:
        print("Returning unauthorized!")
        return HttpResponse('Unauthorized', status=401)
    user_session = request.session['user']
    ret_user = User.objects.get(externalplatform__user_ext_id=user_session["userKey"])
    print("returning :" + str(ret_user))
    return ret_user
