from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from hetaddon.auth.auth_manager import AuthManager

# views #
from .folder_views import *
from .project_views import *
from .document_views import *
from .requirement_views import *
from .section_views import *

#  nasty, remove
mocked = False
inside_atlassian = False

log = logging.getLogger('django')

#################################################################################################################
#####
#####           HTMLS
#####
#################################################################################################################


@ensure_csrf_cookie
def index(request):

    global mocked
    global inside_atlassian

    # mock per backend run
    if not mocked:
        mock_data()
        mocked = True

    AuthManager.authenticate_user(request, inside_atlassian)
    return render(request, 'addon/index.html', {"in_frame": inside_atlassian})


def folder_handler(request, id=None):
    if request.method == 'GET':
        if id:
            return HttpResponseBadRequest("Unexpected ID parameter")
        # return get_folders_json(request)
        return get_folderstructure_json(request)
    elif request.method == 'POST':
        if id:
            return HttpResponseBadRequest()
        return post_folder(request)
    elif request.method == 'PUT':
        return put_folder(request, id)
    elif request.method == 'DELETE':
        return delete_folder(request, id)
    return HttpResponseBadRequest()


def project_handler(request, id=None):
    if request.method == 'GET':
        if id:
            return get_project_json(request, id)
        return get_projects_json(request)
    elif request.method == 'POST':
        if id:
            return HttpResponseBadRequest("Unexpected ID parameter")
        return post_project(request)
    elif request.method == 'PUT':
        return put_project(request, id)
    elif request.method == 'DELETE':
        return delete_project(request, id)
    return HttpResponseBadRequest()


def document_handler(request, id=None):
    if request.method == 'GET':
        if id:
            return get_document_json(request, id)
        return HttpResponseBadRequest("Unsupported operation: GET documents without a specified ID")
    elif request.method == 'POST':
        if id:
            return HttpResponseBadRequest("Found ID parameter on POST request!")
        return post_document(request)
    elif request.method == 'PUT':
        return put_document(request, id)
    elif request.method == 'DELETE':
        return delete_document(request, id)
    return HttpResponseBadRequest()


def requirement_handler(request, id=None):
    if request.method == 'GET':
        if id:
            return get_requirement_json(request, id)
        return HttpResponseBadRequest("Found undefined required ID parameter")
    elif request.method == 'POST':
        if id:
            return HttpResponseBadRequest("Wrong request! Forbidden ID parameter")
        return post_requirement(request)
    elif request.method == 'PUT':
        return put_requirement(request, id)
    elif request.method == 'DELETE':
        return delete_requirement(request, id)
    return HttpResponseBadRequest("Unsupported method!")


def requirement_value_handler(request, id=None):
    if request.method == 'GET':
        if id:
            return get_requirement_value_json(request, id)
        return HttpResponseBadRequest("Found undefined required ID parameter")
    if request.method == 'POST':
        if id:
            return HttpResponseBadRequest("Wrong request! Forbidden ID parameter")
        return post_requirement_value(request)
    if request.method == 'PUT':
        return put_requirement_value(request, id)
    else:
        return HttpResponseBadRequest("Unsupported method!")