from django.http import *
from django.shortcuts import get_object_or_404
from hetaddon.models.data import *
import json
import binascii
from . import utils

log = logging.getLogger('django')


def get_document_json(request, id):

    user = utils.get_user_from_session(request)
    if user is None:
        return HttpResponse('Unauthorized', status=401)

    document = get_object_or_404(Document, pk=id)
    if not utils.user_owns_document(user, document):
        return HttpResponse('Document ' + str(id) + " is not yours!", status=401)

    document_dict = {"id": document.id, "name": document.name, "type": document.type,
                     "size": document.size, "category": document.category, "section_id": document.section_id}
    return JsonResponse(document_dict)


def post_document(request):

    user = utils.get_user_from_session(request)
    if user is None:
        return HttpResponse('Unauthorized', status=401)

    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)
    if not all(k in data for k in ("name", "category", "content", "section_id", "type", "size")):
        return HttpResponseBadRequest("Unexpected structure! Missing required parameters")
    if not data["name"] or not data["category"] or not data["type"] or not data["size"] or not data["section_id"]:
        return HttpResponseBadRequest("Missing required parameters!")

    section = get_object_or_404(Section, pk=data["section_id"])
    if not utils.user_owns_section(user, section):
        return HttpResponse('Section ' + str(section.id) + " is not yours!", status=401)

    binary_content = binascii.a2b_base64(data["content"])
    Document.objects.create(name=data["name"], type=data["type"], size=data["size"], status="None",
                            category=data["category"], content=binary_content, section=section)
    return HttpResponse("Successfully created a new document", status=201)


def put_document(request, id):

    user = utils.get_user_from_session(request)
    if user is None:
        return HttpResponse('Unauthorized', status=401)

    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)
    document = get_object_or_404(Document, pk=id)
    if "name" in data:
        document.name = data["name"]
    if "type" in data:
        document.type = data["type"]
    if "size" in data:
        document.size = data["size"]
    if "category" in data:
        document.category = data["category"]
    if "section_id" in data:
        section = get_object_or_404(Section, pk=data["section_id"])
        if not utils.user_owns_section(user, section):
            return HttpResponse('Section ' + str(section.id) + " is not yours!", status=401)
        document.section = section

    document.save()
    return HttpResponse("Document was successfully updated", status=200)


def delete_document(request, id):

    user = utils.get_user_from_session(request)
    if user is None:
        return HttpResponse('Unauthorized', status=401)

    document = get_object_or_404(Document, pk=id)
    if not utils.user_owns_document(user, document):
        return HttpResponse('Document ' + str(id) + " is not yours!", status=401)

    document.delete()
    return HttpResponse("Document " + str(id) + " was successfully deleted", status=200)


def get_documents_of_project_json(request, id):

    user = utils.get_user_from_session(request)
    if user is None:
        return HttpResponse('Unauthorized', status=401)

    # check if the project exists, return error otherwise
    project = get_object_or_404(Project, pk=id)
    memb = get_object_or_404(project.members.all(), pk=user.id)

    documents_list = list(Document.objects.filter(section__project_id=id))
    documents_list.sort(key=lambda doc: doc.pk)
    documents_json_list = [{"id": documents_list[i].id, "name": documents_list[i].name, "type": documents_list[i].type,
                            "size": documents_list[i].size, "status": documents_list[i].status,
                            "category": documents_list[i].category, "section_id": documents_list[i].section_id}
                           for i in range(0, len(documents_list))]

    return JsonResponse(documents_json_list, safe=False)
