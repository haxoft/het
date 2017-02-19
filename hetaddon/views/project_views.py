from django.http import *
from django.shortcuts import get_object_or_404
from hetaddon.models.data import *
import json

log = logging.getLogger('django')


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