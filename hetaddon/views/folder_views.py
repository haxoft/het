from django.http import *
from django.shortcuts import get_object_or_404
from hetaddon.models.data import *
from . import utils
import json

log = logging.getLogger('django')


def get_folderstructure_json(request):
    user = utils.get_user_from_session(request)
    if user is None:
        return HttpResponse('Unauthorized', status=401)
    root_folders = list(RootFolder.objects.filter(owner_id=user.id))

    result = get_folders_for_folderstructure(root_folders, user)

    return JsonResponse(result, safe=False)


def get_folders_for_folderstructure(folders, user):
    folderstructure = [{"id": folder.pk, "name": folder.name,
                        "folders": get_folders_for_folderstructure(folder.folder_set.all(), user),
                        "projects": get_projects_for_folderstructure(folder.projects.filter(membership__user_id=user.id))}
                       for folder in folders]
    return folderstructure


def get_projects_for_folderstructure(projects):
    return [{"id": project.pk, "name": project.name, "requirements_extracted": project.requirement_set.count() > 0} for project in projects]


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
