from django.http import *
from django.shortcuts import get_object_or_404
from hetaddon.models.data import *
from . import utils
import json


log = logging.getLogger('django')


def get_projects_json(request):

    if 'user' not in request.session:
        return HttpResponse('Unauthorized', status=401)
    user_session = request.session['user']
    user = User.objects.get(externalplatform__user_ext_id=user_session["userKey"])

    # user = utils.get_user_from_session(request)
    # log.debug("found user from session:" + str(user))

    user_projects = list(Project.objects.filter(membership__user_id=user.id))
    log.debug("Found user projects:" + str(user_projects))
    user_projects.sort(key=lambda project: project.pk)

    user_projects_list = []
    user_folders_list = get_user_folders(user)
    log.debug("found user folders:" + str(user_folders_list))
    for i in range(0, len(user_projects)):
        folder = get_folder_of_project(user_projects[i], user)
        if folder is None:
            return HttpResponseServerError("Unable to find folder for project " + str(user_projects[i].id))

        user_projects_list.append({"name": user_projects[i].name,
                                   "created": user_projects[i].created,
                                   "folder_id": folder.id})

    return JsonResponse(user_projects_list, safe=False)


def get_project_json(request, id):

    user = utils.get_user_from_session(request)

    project = get_object_or_404(Project, pk=id)
    # print("all project owners:" + str(project.members.all()))
    get_object_or_404(project.members.all(), id=user.id)

    proj_folder = get_folder_of_project(project, user)
    project_dict = {"name": project.name, "folder_id": proj_folder.id}
    return JsonResponse(project_dict)


def post_project(request):

    user = utils.get_user_from_session(request)

    data = json.loads(request.body.decode('utf-8'))
    if not all(k in data for k in ("name", "parent_folder_id")):
        return HttpResponseBadRequest("Unexpected json structure! 'Name' or 'parent_folder_id' fields are missing")
    if not data["name"] or not data["parent_folder_id"]:
        return HttpResponseBadRequest("Found empty required parameters! 'Name' or 'parent_folder_id' fields are missing")

    folder = get_object_or_404(Folder, pk=data["parent_folder_id"])
    user_folders = get_user_folders(user)
    if folder not in user_folders:
        return HttpResponse('Unauthorized action! Folder ' + str(data["parent_folder_id"]) + ' does not belong to you!',
                            status=401)

    new_project = Project.objects.create(name=data["name"], created=timezone.now())
    Membership.objects.create(user=user, project=new_project)
    ProjectFolder.objects.create(project=new_project, folder=folder)

    return HttpResponse("Successfully created a new project", status=201)


def put_project(request, id):

    user = utils.get_user_from_session(request)

    data = json.loads(request.body.decode('utf-8'))
    project = get_object_or_404(Project, pk=id)
    get_object_or_404(project.members.all(), id=user.id) # check if the user is member of the project

    if "name" in data:
        project.name = data["name"]
    if "parent_folder_id" in data:
        folder = get_object_or_404(Folder, pk=data["parent_folder_id"])
        if not user_owns_folder(user, folder):
            return HttpResponse('Unauthorized action! Folder ' + str(folder.id) + ' does not belong to you!',
                                status=401)
        # remove the old project folder link
        old_folder = get_folder_of_project(project, user)
        get_object_or_404(ProjectFolder, project=project, folder=old_folder).delete()
        ProjectFolder.objects.create(project=project, folder=folder) # create the new link

    project.save()
    return HttpResponse("Updated folder " + str(id), status=200)


def delete_project(request, id):

    user = utils.get_user_from_session(request)

    project = get_object_or_404(Project, pk=id)
    get_object_or_404(project.members.all(), id=user.id) # check if the user is member of the project

    project.delete()
    return HttpResponse("Deleted project " + str(id), status=200)


def user_owns_folder(user, folder):

    user_folders = get_user_folders(user)
    for user_folder in user_folders:
        if user_folder.id == folder.id:
            return True

    return False


def get_folder_of_project(project, user):
    log.debug('finding the folder of project:' + str(project))
    user_folders_list = get_user_folders(user)
    for i in range(0, len(user_folders_list)):
        project_folder_set = ProjectFolder.objects.filter(project=project, folder=user_folders_list[i])
        if project_folder_set:
            if len(project_folder_set) > 1:
                log.error("Found multiple folders for project! Found ProjectFolders:" + str(project_folder_set))
                return None
            log.debug("Found folder:" + str(project_folder_set[0].folder.id) + ", for project:" + str(project.id))
            return project_folder_set[0].folder
    log.error("Found no folder for project! Project:" + str(project))
    return None


def get_user_folders(user):
    user_root_folders = RootFolder.objects.filter(owner=user)
    user_folders = []
    for root_folder in user_root_folders:
        # log.debug("Appending root folder:" + str(root_folder))
        user_folders.append(root_folder)
        add_subfolders(user_folders, root_folder)
    return user_folders


def add_subfolders(subfolders_list, parent_folder):
    subfolders_set = parent_folder.folder_set.all()
    for i in range(0, len(subfolders_set)):
        subfolders_list.append(subfolders_set[i])
        add_subfolders(subfolders_list, subfolders_set[i])

