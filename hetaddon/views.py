from django.shortcuts import render
from .data import *
from django.utils import timezone
from django.http import *
from django.views.decorators.csrf import ensure_csrf_cookie
import binascii
import json

#  nasty, remove
mocked = False


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

    # ...some user retrieval using jwt
    userId = 1
    user_folders_list = Folder.objects.all()  # ... getting folders for a specific user might be tricky
    user_projects_list = Project.objects.all()

    context = {
        'user_folders_list': user_folders_list,
        'user_projects_list': user_projects_list,
    }

    return render(request, 'addon/index.html', context)


#################################################################################################################
#####
#####           Handler
#####
#################################################################################################################


def folder_handler(request, id=None):
    if request.method == 'GET':
        if id:
            return HttpResponseBadRequest()
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
        return HttpResponseBadRequest()
    elif request.method == 'POST':
        if id:
            return HttpResponseBadRequest()
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
        return HttpResponseBadRequest()
    elif request.method == 'POST':
        if id:
            return HttpResponseBadRequest()
        return post_requirement(request)
    elif request.method == 'PUT':
        return put_requirement(request, id)
    elif request.method == 'DELETE':
        return delete_requirement(request, id)
    return HttpResponseBadRequest()


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
    data = json.loads(body_unicode)
    if not all(k in data for k in ("name", "parent_folder_id")):
        return HttpResponseBadRequest("Unexpected structure! Missing name or parent folder id!")
    if not data["name"]:
        return HttpResponseBadRequest("Found empty required parameter: name")
    parent_folder_id = data["parent_folder_id"]
    # todo: return error upon wrong ID reception
    parent = None if parent_folder_id is None else Folder.objects.get(pk=parent_folder_id)
    Folder.objects.create(name=data["name"], parent_folder=parent)
    return HttpResponse("Folder successfully created", status=201)


def put_folder(request, id):
    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)
    folder = Folder.objects.get(pk=id)
    if not folder:
        return HttpResponseNotFound()
    if data["name"]:
        folder.name = data["name"]
    if data["parent_folder_id"]:
        parent = Folder.objects.get(pk=data["parent_folder_id"])
        if not folder:
            return HttpResponseBadRequest()
        folder.parent_folder = parent
    folder.save()
    return HttpResponse("Updated", status=200)


def delete_folder(request, id):
    folder = Folder.objects.get(pk=id)
    if folder:
        folder.delete()
        return HttpResponse("Deleted", status=200)
    return HttpResponseNotFound("Unable to find folder with id=" + str(id))


#################################################################################################################
#####
#####           Project Views
#####
#################################################################################################################


def get_projects_json(request):
    projects = list(Project.objects.all())
    projects.sort(key=lambda project: project.pk)
    projects_list = [{"name": projects[i].name, "folder": projects[i].folder.name}
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
    folder = Folder.objects.get(pk=data["parent_folder_id"])
    if not folder:
        return HttpResponseBadRequest("Parent folder with id=" + str(data["parent_folder_id"]) + " not found!")
    Project.objects.create(name=data["name"], created=timezone.now(), folder=folder)
    return HttpResponse("Successfully created a new project", status=201)


def put_project(request, id):
    data = json.loads(request.body.decode('utf-8'))
    project = Project.objects.get(pk=id)
    if not project:
        return HttpResponseNotFound("Found no project with id=" + str(id))
    if data["name"]:
        project.name = data["name"]
    if data["parent_folder_id"]:
        folder = Folder.objects.get(pk=data["parent_folder_id"])
        if not folder:
            return HttpResponseBadRequest("Found no folder with id=" + str(data["parent_folder_id"]))
        project.folder = folder
    project.save()
    return HttpResponse("Updated", status=200)


def delete_project(request, id):
    project = Project.objects.get(pk=id)
    if project:
        project.delete()
        return HttpResponse("Deleted", status=200)
    return HttpResponseNotFound()


#################################################################################################################
#####
#####           Document Views
#####
#################################################################################################################


def get_document_json(request, id):
    document = Document.objects.get(pk=id)
    document_dict = {"id": document.id, "name": document.name, "type": document.type,
                     "size": document.size, "category": document.category, "section_id": document.section_id}
    return JsonResponse(document_dict)


def post_document(request):
    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)
    if not all(k in data for k in ("name", "category", "content", "project_id", "type", "size")):
        return HttpResponseBadRequest(JsonResponse({"errors": "Fehler"}))
    project = Project.objects.get(pk=data["project_id"])
    if not project:
        return HttpResponseBadRequest()
    # temp demo code
    section = project.section_set.first()
    # /temp demo code
    binary_content = binascii.a2b_base64(data["content"])
    Document.objects.create(name=data["name"], type=data["type"], size=data["size"], status="None",
                            category=data["category"],
                            content=binary_content, section=section)
    return HttpResponse("Created", status=201)


def put_document(request, id):
    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)
    document = Document.objects.get(pk=id)
    if not document:
        return HttpResponseNotFound()
    if data["name"]:
        document.name = data["name"]
    if data["type"]:
        document.type = data["type"]
    if data["size"]:
        document.size = data["size"]
    if data["category"]:
        document.category = data["category"]
    if data["section_id"]:
        section = Section.objects.get(pk=data["section_id"])
        if not section:
            return HttpResponseBadRequest()
        document.section = section
    document.save()
    return HttpResponse("Updated", status=200)


def delete_document(request, id):
    document = Document.objects.get(pk=id)
    if document:
        document.delete()
        return HttpResponse("Deleted", status=200)
    return HttpResponseNotFound()


def get_documents_of_project_json(request, id):
    documents_list = list(Document.objects.filter(section__project_id=id))
    documents_list.sort(key=lambda doc: doc.pk)
    documents_json_list = [{"id": documents_list[i].id, "name": documents_list[i].name,
                          "type": documents_list[i].type, "size": documents_list[i].size,
                          "status": documents_list[i].status, "category": documents_list[i].category,
                          "section_id": documents_list[i].section_id} for i in range(0, len(documents_list))]
    return JsonResponse(documents_json_list, safe=False)


#################################################################################################################
#####
#####           Requirement Views
#####
#################################################################################################################


def get_requirement_json(request, id):
    requirement = Requirement.objects.get(pk=id)
    requirement_dict = {"id": requirement.id, "name": requirement.name,
                        "values": [r.value for r in Requirement.objects.all() if r.name == requirement.name],
                        "disabled": requirement.disabled}
    return JsonResponse(requirement_dict)


def post_requirement(request):
    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)
    if not all(k in data for k in ("name", "values", "project_id")):
        return HttpResponseBadRequest("Missing required parameters!")
    project = Project.objects.get(pk=data["project_id"])
    if not project:
        return HttpResponseBadRequest()
    Requirement.objects.create(name=data["name"], values=data["values"], project=project)
    return HttpResponse("Created", status=201)


def put_requirement(request, id):
    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)
    requirement = Requirement.objects.get(pk=id)
    if not requirement:
        return HttpResponseNotFound()
    if data["name"]:
        requirement.name = data["name"]
    if data["values"]:
        requirement.type = data["values"]
    if data["disabled"]:
        requirement.disabled = data["disabled"]
    requirement.save()
    return HttpResponse("Updated", status=200)


def delete_requirement(request, id):
    requirement = Requirement.objects.get(pk=id)
    if requirement:
        requirement.delete()
        return HttpResponse("Deleted", status=200)
    return HttpResponseNotFound()


def get_requirements_of_project_json(request, id):
    requirements_list = list(Requirement.objects.filter(project_id=id))
    requirements_list.sort(key=lambda req: req.pk)
    requirements_json_list = [{"id": requirements_list[i].id, "name": requirements_list[i].name,
                             "values": [r.value for r in requirements_list if r.name == requirements_list[i].name],
                             "document": requirements_list[i].document_id, "disabled": requirements_list[i].disabled}
                         for i in range(0, len(requirements_list))]
    return JsonResponse(requirements_json_list, safe=False)
