from django.http import *
from django.shortcuts import get_object_or_404
from hetaddon.models.data import *
from . import utils
import json

log = logging.getLogger('django')


def get_folderstructure_json(request, id=None):

    user = utils.get_user_from_session(request)
    if user is None:
        return HttpResponse('Unauthorized', status=401)

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

        root_folders = list(RootFolder.objects.filter(owner_id=user.id))
        # print("found root folders:" + str(root_folders))

        root_folders.sort(key=lambda f: f.pk)
        for folder in root_folders:
            folder_dict = {"id": folder.pk, "name": folder.name, "folders": [], "projects": []}
            project_set = folder.projects.all()
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
        project_set = folder.projects.all()
        subfolder_set = folder.folder_set.all()
        if project_set:
            add_projects_to_folder_structure(folder_dict.get("projects"), project_set)
        if subfolder_set:
            add_folders_to_folder_structure(folder_dict.get("folders"), subfolder_set)
        list.append(folder_dict)


def post_folder(request):

    user = utils.get_user_from_session(request)
    if user is None:
        return HttpResponse('Unauthorized', status=401)

    body_unicode = request.body.decode('utf-8')
    print("Received folder:" + body_unicode)
    data = json.loads(body_unicode)
    if not all(k in data for k in ("name", "parent_folder_id")):
        return HttpResponseBadRequest("Unexpected structure! Missing name or parent folder id!")
    if not data["name"]:
        return HttpResponseBadRequest("Found empty required parameter: name")

    parent_folder = None if data["parent_folder_id"] is None else get_object_or_404(Folder, pk=data["parent_folder_id"])
    if parent_folder is not None:
        root = get_root_folder(parent_folder)
        if root.rootfolder.owner.id != user.id:
            return HttpResponse(('Unauthorized! Parent folder [' + str(parent_folder.id) + '] is not yours!'), status=401)
        else:
            Folder.objects.create(name=data["name"], parent_folder=parent_folder)
    else:  # is a root folder
        RootFolder.objects.create(name=data["name"], parent_folder=None, owner=user)

    return HttpResponse("Folder successfully created", status=201)


def get_root_folder(folder):

    if folder.parent_folder is None:
        return folder
    else:
        return get_root_folder(folder.parent_folder)


def put_folder(request, id):

    user = utils.get_user_from_session(request)
    if user is None:
        return HttpResponse('Unauthorized', status=401)

    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)
    folder = get_object_or_404(Folder, pk=id)
    if "name" in data:
        folder.name = data["name"]
    if "parent_folder_id" in data:
        parent = get_object_or_404(Folder, pk=data["parent_folder_id"])
        folder.parent_folder = parent
        # todo test that the root folder belongs to the user in session
    folder.save()
    return HttpResponse("Updated folder " + str(id), status=200)


def delete_folder(request, id):

    user = utils.get_user_from_session(request)
    if user is None:
        return HttpResponse('Unauthorized', status=401)

    user_session = request.session['user']
    user = User.objects.get(externalplatform__user_ext_id=user_session["userKey"])

    folder = get_object_or_404(Folder, pk=id)

    root = folder    # print("attempt to delete folder:" + str(folder))
    if root.parent_folder is not None:
        root = get_root_folder(root)

    if root.rootfolder.owner.id != user.id:
        return HttpResponse(('Unauthorized! Folder [' + str(id) + '] is not yours!'), status=401)

    folder.delete()
    return HttpResponse("Deleted folder " + str(id), status=200)
