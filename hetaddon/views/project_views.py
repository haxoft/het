from django.http import *
from django.shortcuts import get_object_or_404
from hetaddon.models.data import *
from . import utils
from hetaddon.search import *
import json


log = logging.getLogger('django')


def get_projects_json(request):

    user = utils.get_user_from_session(request)
    if user is None:
        return HttpResponse('Unauthorized', status=401)

    user_projects = list(Project.objects.filter(membership__user_id=user.id))
    log.debug("Found user projects:" + str(user_projects))
    user_projects.sort(key=lambda project: project.pk)

    user_projects_list = []
    user_folders_list = utils.get_user_folders(user)
    log.debug("found user folders:" + str(user_folders_list))
    for i in range(0, len(user_projects)):
        folder = utils.get_folder_of_project(user_projects[i], user)
        if folder is None:
            return HttpResponseServerError("Unable to find folder for project " + str(user_projects[i].id))

        user_projects_list.append({"name": user_projects[i].name,
                                   "created": user_projects[i].created,
                                   "folder_id": folder.id,
                                   "requirements_extracted": user_projects[i].requirement_set.count()})

    return JsonResponse(user_projects_list, safe=False)


def get_project_json(request, id):

    user = utils.get_user_from_session(request)
    if user is None:
        return HttpResponse('Unauthorized', status=401)

    project = get_object_or_404(Project, pk=id)
    get_object_or_404(project.members.all(), id=user.id)

    proj_folder = utils.get_folder_of_project(project, user)
    project_dict = {"name": project.name,
                    "folder_id": proj_folder.id,
                    "requirements_extracted": project.requirement_set.count() > 0}
    return JsonResponse(project_dict)


def post_project(request):

    user = utils.get_user_from_session(request)
    if user is None:
        return HttpResponse('Unauthorized', status=401)

    data = json.loads(request.body.decode('utf-8'))
    if not all(k in data for k in ("name", "parent_folder_id")):
        return HttpResponseBadRequest("Unexpected json structure! 'Name' or 'parent_folder_id' fields are missing")
    if not data["name"] or not data["parent_folder_id"]:
        return HttpResponseBadRequest("Found empty required parameters! 'Name' or 'parent_folder_id' fields are missing")

    folder = get_object_or_404(Folder, pk=data["parent_folder_id"])
    user_folders = utils.get_user_folders(user)
    if folder.id not in [f.id for f in user_folders]:
        return HttpResponse('Unauthorized action! Folder ' + str(data["parent_folder_id"]) + ' does not belong to you!',
                            status=401)

    new_project = Project.objects.create(name=data["name"], created=timezone.now())
    Membership.objects.create(user=user, project=new_project)
    ProjectFolder.objects.create(project=new_project, folder=folder)

    return HttpResponse("Successfully created a new project", status=201)


def put_project(request, id):

    user = utils.get_user_from_session(request)
    if user is None:
        return HttpResponse('Unauthorized', status=401)

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
        old_folder = utils.get_folder_of_project(project, user)
        get_object_or_404(ProjectFolder, project=project, folder=old_folder).delete()
        ProjectFolder.objects.create(project=project, folder=folder) # create the new link

    project.save()
    return HttpResponse("Updated folder " + str(id), status=200)


def delete_project(request, id):

    user = utils.get_user_from_session(request)
    if user is None:
        return HttpResponse('Unauthorized', status=401)

    project = get_object_or_404(Project, pk=id)
    get_object_or_404(project.members.all(), id=user.id) # check if the user is member of the project

    project.delete()
    return HttpResponse("Deleted project " + str(id), status=200)


def analyze_project(request, id):
    user = utils.get_user_from_session(request)
    if user is None:
        return HttpResponse('Unauthorized', status=401)

    project = get_object_or_404(Project, pk=id)
    get_object_or_404(project.members.all(), id=user.id)
    documents = Document.objects.filter(section__project_id=project.id)

    extractor = RequirementExtractor(documents)
    extractor.do_extraction()
    extractor_documents = extractor.documents

    for extractor_document in extractor_documents:
        for requirement in extractor_document.requirements:
            name = requirement.name
            values_shown = requirement.values_shown
            ranked_results = requirement.ranked_results
            requirement = Requirement.objects.create(name=name, project=project, values_shown=values_shown)
            for ranked_result in ranked_results:
                RequirementValue.objects.create(value=ranked_result.value, rating=ranked_result.rating,
                                                document=extractor_document.document, requirement=requirement)
    return HttpResponse("Analysis was successful", status=200)


def user_owns_folder(user, folder):

    user_folders = utils.get_user_folders(user)
    for user_folder in user_folders:
        if user_folder.id == folder.id:
            return True

    return False
