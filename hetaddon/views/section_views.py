from django.http import *
from django.shortcuts import get_object_or_404
from hetaddon.models.data import *
import json
import binascii
from . import utils

log = logging.getLogger('django')


def get_section_json(request, id):

    user = utils.get_user_from_session(request)
    if user is None:
        return HttpResponse('Unauthorized', status=401)

    section = get_object_or_404(Section, pk=id)
    if not utils.user_owns_section(user, section):
        return HttpResponse('Section ' + str(id) + " is not yours!", status=401)

    section_documents = section.document_set
    section_documents.sort(key=lambda doc: doc.pk)

    documents_json_list = [{"id": document.id, "name": document.name, "type": document.type,
                            "size": document.size, "status": document.status, "category": document.category,
                            "section_id": document.section_id}
                           for document in section_documents]
    section_dict = {"id": section.id, "name": section.name, "documents": documents_json_list}
    return JsonResponse(section_dict)


def post_section(request):

    user = utils.get_user_from_session(request)
    if user is None:
        return HttpResponse('Unauthorized', status=401)

    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)
    if not all(k in data for k in ("name", "project_id")):
        return HttpResponseBadRequest("Unexpected structure! Missing required parameters")
    if not data["name"] or not data["project_id"]:
        return HttpResponseBadRequest("Missing required parameters!")

    project = get_object_or_404(Project, pk=data["project_id"])
    get_object_or_404(Membership, user=user, project=project)

    Section.objects.create(name=data["name"], project=project)
    return HttpResponse("Successfully created a new section", status=201)


def put_section(request, id):

    user = utils.get_user_from_session(request)
    if user is None:
        return HttpResponse('Unauthorized', status=401)

    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)
    section = get_object_or_404(Section, pk=id)
    if "name" in data:
        section.name = data["name"]
    if "project_id" in data:
        project = get_object_or_404(Section, pk=data["section_id"])
        get_object_or_404(Membership, user=user, project=project)
        section.project = project

    section.save()
    return HttpResponse("Section was successfully updated", status=200)


def delete_section(request, id):

    user = utils.get_user_from_session(request)
    if user is None:
        return HttpResponse('Unauthorized', status=401)

    section = get_object_or_404(Section, pk=id)
    if not utils.user_owns_section(user, section):
        return HttpResponse('Section ' + str(id) + " is not yours!", status=401)

    section.delete()
    return HttpResponse("Section " + str(id) + " was successfully deleted", status=200)


def get_sections_of_project_json(request, id):

    user = utils.get_user_from_session(request)
    if user is None:
        return HttpResponse('Unauthorized', status=401)

    # check if the project exists, return error otherwise
    project = get_object_or_404(Project, pk=id)
    get_object_or_404(project.members.all(), pk=user.id)

    sections = project.section_set

    sections_json_list = []
    for section in sections:
        section_documents = list(section.document_set)
        section_documents.sort(key=lambda doc: doc.pk)
        documents_json_list = [{"id": document.id, "name": document.name, "type": document.type,
                                "size": document.size, "status": document.status, "category": document.category,
                                "section_id": document.section_id}
                               for document in section_documents]
        section_dict = {"id": section.id, "name": section.name, "documents": documents_json_list}
        sections_json_list.append(section_dict)

    return JsonResponse(sections_json_list, safe=False)