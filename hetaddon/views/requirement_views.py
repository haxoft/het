from django.http import *
from django.shortcuts import get_object_or_404
from hetaddon.models.data import *
import json
from . import utils

log = logging.getLogger('django')


def get_requirement_json(request, id):

    user = utils.get_user_from_session(request)
    if user is None:
        return HttpResponse('Unauthorized', status=401)

    requirement = get_object_or_404(Requirement, pk=id)
    get_object_or_404(Membership, user=user, project=requirement.project) # check if the user "owns" the requirement

    values_list = RequirementValue.objects.filter(requirement_id=id)
    requirement_dict = {"id": requirement.id, "name": requirement.name, "project_id": requirement.project.id,
                        "values": [{"id": values_list[i].id, "value": values_list[i].value,
                                    "disabled": values_list[i].disabled, "document_id": values_list[i].document_id}
                                   for i in range(0, len(values_list))],
                        "values_shown": requirement.values_shown}
    return JsonResponse(requirement_dict)


def post_requirement(request):

    user = utils.get_user_from_session(request)
    if user is None:
        return HttpResponse('Unauthorized', status=401)

    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)
    if not all(k in data for k in ("name", "project_id", "values", "values_shown")):
        return HttpResponseBadRequest("Missing required parameters!Expected:[name, project_id, values, values_shown]")
    project = get_object_or_404(Project, pk=data["project_id"])
    get_object_or_404(Membership, user=user, project=project) # check if the user is member of this project

    # todo check structure correctness of each dict in values
    values_list = data["values"]
    req = Requirement.objects.create(name=data["name"], project=project, values_shown=data["values_shown"])
    for i in range(0, len(values_list)):
        value_dict = values_list[i]
        doc = get_object_or_404(Document, pk=value_dict["document_id"])
        RequirementValue.objects.create(value=value_dict["value"], disabled=value_dict["disabled"],
                                        requirement=req, document=doc, rating=value_dict["rating"])

    return HttpResponse("Requirement was successfully created.", status=201)


def put_requirement(request, id):

    user = utils.get_user_from_session(request)
    if user is None:
        return HttpResponse('Unauthorized', status=401)

    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)
    requirement = get_object_or_404(Requirement, pk=id)
    get_object_or_404(Membership, user=user, project=requirement.project)

    if "name" in data:
        requirement.name = data["name"]
    if "values_shown" in data:
        values_shown = data["values_shown"]
        requirement_values = requirement.requirementvalue_set
        if requirement_values.count() >= values_shown:
            requirement.values_shown = values_shown
            while requirement_values.filter(rejected=False).count() < values_shown:
                rejected_value = requirement_values.filter(rejected=True).order_by("-rating")[0]
                rejected_value.rejected = False
                rejected_value.save()
    requirement.save()

    return HttpResponse("Requirement was successfully updated", status=200)


def delete_requirement(request, id):

    user = utils.get_user_from_session(request)
    if user is None:
        return HttpResponse('Unauthorized', status=401)

    requirement = get_object_or_404(Requirement, pk=id)
    get_object_or_404(Membership, user=user, project=requirement.project)

    requirement.delete()
    return HttpResponse("Requirement was successfully deleted", status=200)


def get_requirements_of_project_json(request, id):

    user = utils.get_user_from_session(request)
    if user is None:
        return HttpResponse('Unauthorized', status=401)

    # check if the project exists, and if it belongs to the user
    project = get_object_or_404(Project, pk=id)
    get_object_or_404(Membership, user=user, project=project)

    requirements_list = list(Requirement.objects.filter(project_id=id))
    requirements_list.sort(key=lambda req: req.pk)

    requirements_json_list = []
    for i in range(0, len(requirements_list)):
        req = requirements_list[i]
        unrejected_values_list = list(RequirementValue.objects.filter(requirement_id=req.id, rejected=False))
        unrejected_values_list.sort(key=lambda val: val.rating, reverse=True)
        values_json_list = []
        values_shown = min(req.values_shown, len(unrejected_values_list))
        for j in range(0, values_shown):
            values_json_list.append({"id": unrejected_values_list[j].id, "value": unrejected_values_list[j].value,
                                     "disabled": unrejected_values_list[j].disabled, "document": unrejected_values_list[j].document_id })
        requirements_json_list.append({"id": req.id, "name": req.name, "values": values_json_list, "values_shown": req.values_shown})

    return JsonResponse(requirements_json_list, safe=False)


def get_requirement_value_json(request, id):

    user = utils.get_user_from_session(request)
    if user is None:
        return HttpResponse('Unauthorized', status=401)

    req_value = get_object_or_404(RequirementValue, pk=id)
    get_object_or_404(Membership, user=user, project=req_value.requirement.project)

    req_value_dict = {"id": req_value.id, "value": req_value.name, "disabled": req_value.project.id,
                      "requirement_id": req_value.requirement_id, "document_id": req_value.document_id,
                      "rating": req_value.rating}
    return JsonResponse(req_value_dict)


def post_requirement_value(request):

    user = utils.get_user_from_session(request)
    if user is None:
        return HttpResponse('Unauthorized', status=401)

    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)
    if not all(k in data for k in ("value", "requirement_id", "document_id", "rating")):
        return HttpResponseBadRequest("Missing required parameters!Expected:[value, requirement_id, document_id, rating]")

    requirement = get_object_or_404(Requirement, pk=data["requirement_id"])
    get_object_or_404(Membership, user=user, project=requirement.project)

    document = get_object_or_404(Document, pk=data["document_id"])
    get_object_or_404(Membership, user=user, project=document.section.project)

    RequirementValue.objects.create(value=data["value"], requirement=requirement, document=document, rating=data["rating"])
    return HttpResponse("Requirement was successfully created.", status=201)


def put_requirement_value(request, id):

    user = utils.get_user_from_session(request)
    if user is None:
        return HttpResponse('Unauthorized', status=401)

    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)
    req_value = get_object_or_404(RequirementValue, pk=id)
    get_object_or_404(Membership, user=user, project=req_value.requirement.project)

    if "value" in data:
        req_value.value = data["value"]
    if "document_id" in data:
        req_value.document = get_object_or_404(Document, pk=data["document_id"])
        get_object_or_404(Membership, user=user, project=req_value.document.section.project)
    if "disabled" in data:
        req_value.disabled = data["disabled"]
    if "requirement_id" in data:
        req_value.requirement = get_object_or_404(Requirement, pk=data["requirement_id"])
    if "rejected" in data:
        req_value.rejected = True
        requirement = req_value.requirement
        unrejected_values = requirement.requirementvalue_set.filter(rejected=False).exclude(id=req_value.id)
        if unrejected_values.count() < requirement.values_shown:
            rejected_values = requirement.requirementvalue_set.filter(rejected=True).order_by("-rating")
            if rejected_values.count() == 0:
                req_value.rejected = False
            else:
                best_rejected_value = rejected_values[0]
                best_rejected_value.rejected = False
                best_rejected_value.save()

    req_value.save()
    return HttpResponse("Requirement was successfully updated", status=200)