from django.shortcuts import render
from .data import *
from django.utils import timezone
from django.http import *
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import get_object_or_404

import binascii
import json
from hetaddon.auth.authManager import AuthManager
import logging

#  nasty, remove
mocked = False
log = logging.getLogger('django')
inside_atlassian = False


#################################################################################################################
#####
#####           HTMLS
#####
#################################################################################################################


@ensure_csrf_cookie
def index(request):

    global mocked

    # mock per backend run
    if not mocked:
        mock_data()
        mocked = True

    AuthManager.authenticate_user(request)
    return render(request, 'addon/index.html', {"in_frame": inside_atlassian})


#################################################################################################################
#####
#####           Handler
#####
#################################################################################################################


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
            return HttpResponseBadRequest("Found undefined required ID parameter")
        return post_requirement(request)
    elif request.method == 'PUT':
        return put_requirement(request, id)
    elif request.method == 'DELETE':
        return delete_requirement(request, id)
    return HttpResponseBadRequest("Unsupported method!")


def requirement_value_handler(request, id=None):
    if request.method == 'GET':
        return get_requirement_value_json(request, id)
    if request.method == 'POST':
        return post_requirement_value(request)
    if request.method == 'PUT':
        return put_requirement_value(request, id)
    else:
        return HttpResponseBadRequest("Unsupported method!")

#################################################################################################################
#####
#####           Folder Views
#####
#################################################################################################################


def get_folderstructure_json(request, id=None):
    result = []
    # this branch is never called?
    if id:
        project = list(Project.objects.filter(pk=id))
        projects_path = (list(Folder.objects.filter(pk=project[0].folder_id)))
        while projects_path[-1].parent_folder_id is not None:
            projects_path.extend(list(Folder.objects.filter(pk=projects_path[-1].parent_folder_id)))
        folder = projects_path.pop()
        result = {"id": folder.pk, "name": folder.name, "folders": [], "projects": []}
        folders_array = result.get("folders")
        while projects_path:
            folder = projects_path.pop()
            temp = {"id": folder.pk, "name": folder.name, "folders": [], "projects": []}
            folders_array.append(temp)
            folders_array = temp.get("folders")
            project_list = temp.get("projects")
        add_projects_to_folder_structure(project_list, project)
    else:

        # TODO return only folders that belong to user in the session
        user_context = request.session['user']
        log.info("Found user session:" + str(user_context))

        top_folders = list(Folder.objects.filter(parent_folder=None))
        top_folders.sort(key=lambda f: f.pk)
        for folder in top_folders:
            folder_dict = {"id": folder.pk, "name": folder.name, "folders": [], "projects": []}
            project_set = folder.project_set.all()
            folder_set = folder.folder_set.all()
            if project_set:
                add_projects_to_folder_structure(folder_dict.get("projects"), project_set)
            if folder_set:
                add_folders_to_folder_structure(folder_dict.get("folders"), folder_set)
            result.append(folder_dict)

    return JsonResponse(result, safe=False)


def add_projects_to_folder_structure(list, project_set):
    for project in project_set:
        project_dict = {"id": project.pk, "name": project.name, "requirementsExtracted": False}
        if project.requirement_set.all():
            project_dict["requirementsExtracted"] = True
        list.append(project_dict)


def add_folders_to_folder_structure(list, folder_set):
    for folder in folder_set:
        folder_dict = {"id": folder.pk, "name": folder.name, "folders": [], "projects": []}
        project_set = folder.project_set.all()
        subfolder_set = folder.folder_set.all()
        if project_set:
            add_projects_to_folder_structure(folder_dict.get("projects"), project_set)
        if subfolder_set:
            add_folders_to_folder_structure(folder_dict.get("folders"), subfolder_set)
        list.append(folder_dict)


# not in use - remove?
def get_folders_json(request):
    folders = list(Folder.objects.all())
    folders.sort(key=lambda folder: folder.pk)
    folders_list = [{"name": folders[i].name, "parent_folder_id": folders[i].parent_folder.id}
                    for i in range(0, len(folders))]

    return JsonResponse(folders_list, safe=False)


def post_folder(request):
    body_unicode = request.body.decode('utf-8')
    print(body_unicode)
    data = json.loads(body_unicode)
    if not all(k in data for k in ("name", "parent_folder_id")):
        return HttpResponseBadRequest("Unexpected structure! Missing name or parent folder id!")
    if not data["name"]:
        return HttpResponseBadRequest("Found empty required parameter: name")
    parent_folder_id = data["parent_folder_id"]
    # todo: return error upon wrong ID reception
    parent = None if parent_folder_id is None else get_object_or_404(Folder, pk=parent_folder_id)
    Folder.objects.create(name=data["name"], parent_folder=parent)
    return HttpResponse("Folder successfully created", status=201)


def put_folder(request, id):
    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)
    folder = get_object_or_404(Folder, pk=id)
    if "name" in data:
        folder.name = data["name"]
    if "parent_folder_id" in data:
        parent = get_object_or_404(Folder, pk=data["parent_folder_id"])
        folder.parent_folder = parent
    folder.save()
    return HttpResponse("Updated", status=200)


def delete_folder(request, id):
    folder = get_object_or_404(Folder, pk=id)
    folder.delete()
    return HttpResponse("Deleted", status=200)


#################################################################################################################
#####
#####           Project Views
#####
#################################################################################################################


def get_projects_json(request):
    projects = list(Project.objects.all())
    projects.sort(key=lambda project: project.pk)
    projects_list = [{"name": projects[i].name, "created": projects[i].created, "folder_id": projects[i].folder.id}
                     for i in range(0, len(projects))]
    return JsonResponse(projects_list, safe=False)


def get_project_json(request, id):
    project = Project.objects.get(pk=id)
    project_dict = {"name": project.name, "folder": project.folder.name}
    return JsonResponse(project_dict)


def post_project(request):
    data = json.loads(request.body.decode('utf-8'))
    if not all(k in data for k in ("name", "parent_folder_id")):
        return HttpResponseBadRequest("Unexpected json structure! 'Name' or 'parent_folder_id' fields are missing")
    if not data["name"] or not data["parent_folder_id"]:
        return HttpResponseBadRequest("Found empty required parameters! 'Name' or 'parent_folder_id' fields are missing")
    folder = get_object_or_404(Folder, pk=data["parent_folder_id"])
    Project.objects.create(name=data["name"], created=timezone.now(), folder=folder)
    return HttpResponse("Successfully created a new project", status=201)


def put_project(request, id):
    data = json.loads(request.body.decode('utf-8'))
    project = get_object_or_404(Project, pk=id)
    if "name" in data:
        project.name = data["name"]
    if "parent_folder_id" in data:
        folder = get_object_or_404(Folder, pk=data["parent_folder_id"])
        project.folder = folder
    project.save()
    return HttpResponse("Updated", status=200)


def delete_project(request, id):
    project = get_object_or_404(Project, pk=id)
    project.delete()
    return HttpResponse("Deleted", status=200)


#################################################################################################################
#####
#####           Document Views
#####
#################################################################################################################


def get_document_json(request, id):
    document = get_object_or_404(Document, pk=id)
    document_dict = {"id": document.id, "name": document.name, "type": document.type,
                     "size": document.size, "category": document.category, "section_id": document.section_id}
    return JsonResponse(document_dict)


def post_document(request):
    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)
    if not all(k in data for k in ("name", "category", "content", "section_id", "type", "size")):
        return HttpResponseBadRequest("Unexpected structure! Missing required parameters")
    if not data["name"] or not data["category"] or not data["type"] or not data["size"] or not data["section_id"]:
        return HttpResponseBadRequest("Missing required parameters!")
    section = get_object_or_404(Section, pk=data["section_id"])
    binary_content = binascii.a2b_base64(data["content"])
    Document.objects.create(name=data["name"], type=data["type"], size=data["size"], status="None",
                            category=data["category"],
                            content=binary_content, section=section)
    return HttpResponse("Successfully created a new document", status=201)


def put_document(request, id):
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
        document.section = section
    document.save()
    return HttpResponse("Document was successfully updated", status=200)


def delete_document(request, id):
    document = get_object_or_404(Document, pk=id)
    document.delete()
    return HttpResponse("Document was successfully deleted", status=200)


def get_documents_of_project_json(request, id):

    # check if the document exists, return error otherwise
    get_object_or_404(Project, pk=id)

    documents_list = list(Document.objects.filter(section__project_id=id))
    documents_list.sort(key=lambda doc: doc.pk)
    documents_json_list = [{"id": documents_list[i].id, "name": documents_list[i].name, "type": documents_list[i].type,
                            "size": documents_list[i].size, "status": documents_list[i].status,
                            "category": documents_list[i].category, "section_id": documents_list[i].section_id}
                           for i in range(0, len(documents_list))]

    return JsonResponse(documents_json_list, safe=False)


#################################################################################################################
#####
#####           Requirement Views
#####
#################################################################################################################


def get_requirement_json(request, id):
    requirement = get_object_or_404(Requirement, pk=id)
    values_list = RequirementValue.objects.filter(requirement_id=id)
    requirement_dict = {"id": requirement.id, "name": requirement.name, "project_id": requirement.project.id,
                        "values": [{"id": values_list[i].id, "value": values_list[i].value,
                                    "disabled": values_list[i].disabled, "document_id": values_list[i].document_id}
                                   for i in range(0, len(values_list))]}
    return JsonResponse(requirement_dict)


def post_requirement(request):
    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)
    if not all(k in data for k in ("name", "project_id", "values")):
        return HttpResponseBadRequest("Missing required parameters!Expected:[name, project_id, values]")
    project = get_object_or_404(Project, pk=data["project_id"])

    # todo check structure correctness of each dict in values
    values_list = data["values"]
    req = Requirement.objects.create(name=data["name"], project=project)
    for i in range(0, len(values_list)):
        value_dict = values_list[i]
        doc = get_object_or_404(Document, pk=value_dict["document_id"])
        RequirementValue.objects.create(value=value_dict["value"], disabled=value_dict["disabled"],
                                        requirement=req, document=doc)

    return HttpResponse("Requirement was successfully created.", status=201)


def put_requirement(request, id):
    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)
    requirement = get_object_or_404(Requirement, pk=id)
    if "name" in data:
        requirement.name = data["name"]
    requirement.save()
    return HttpResponse("Requirement was successfully updated", status=200)


def delete_requirement(request, id):
    requirement = get_object_or_404(Requirement, pk=id)
    requirement.delete()
    return HttpResponse("Requirement was successfully deleted", status=200)


def get_requirements_of_project_json(request, id):

    # check if the project exists, return error otherwise
    get_object_or_404(Project, pk=id)

    requirements_list = list(Requirement.objects.filter(project_id=id))
    requirements_list.sort(key=lambda req: req.pk)

    requirements_json_list = []
    for i in range(0, len(requirements_list)):
        req = requirements_list[i]
        values_list = list(RequirementValue.objects.filter(requirement_id=req.id))
        values_json_list = []
        for j in range(0, len(values_list)):
            values_json_list.append({"id": values_list[j].id, "value": values_list[j].value,
                                     "disabled": values_list[j].disabled, "document": values_list[j].document_id })
        requirements_json_list.append({"id": req.id, "name": req.name, "values": values_json_list})

    return JsonResponse(requirements_json_list, safe=False)


def get_requirement_value_json(request, id):
    req_value = get_object_or_404(RequirementValue, pk=id)
    req_value_dict = {"id": req_value.id, "value": req_value.name, "disabled": req_value.project.id,
                        "requirement_id": req_value.requirement_id, "document_id": req_value.document_id}
    return JsonResponse(req_value_dict)


def post_requirement_value(request):
    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)
    if not all(k in data for k in ("value", "requirement_id", "document_id")):
        return HttpResponseBadRequest("Missing required parameters!Expected:[value, requirement_id, document_id]")
    requirement = get_object_or_404(Requirement, pk=data["requirement_id"])
    document = get_object_or_404(Document, pk=data["document_id"])
    RequirementValue.objects.create(value=data["value"], requirement=requirement, document=document)

    return HttpResponse("Requirement was successfully created.", status=201)


def put_requirement_value(request, id):
    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)
    req_value = get_object_or_404(RequirementValue, pk=id)
    if "value" in data:
        req_value.value = data["value"]
    if "document_id" in data:
        req_value.document = get_object_or_404(Document, pk=data["document_id"])
    if "disabled" in data:
        req_value.disabled = data["disabled"]
    if "requirement_id" in data:
        req_value.requirement = get_object_or_404(Requirement, pk=data["requirement_id"])
    req_value.save()
    return HttpResponse("Requirement was successfully updated", status=200)