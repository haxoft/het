from django.shortcuts import render
from .models import *
from django.utils import timezone
from django.http import *
from django.views.decorators.csrf import csrf_exempt
import binascii
import json
import psycopg2

#  nasty, remove
mocked = False


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
        return delete_project(request, id)
    return HttpResponseBadRequest()


def get_folderstructure_json(request, id=None):
    result = []
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


def get_folders_json(request):
    folders_list = list(Folder.objects.all())
    folders_list.sort(key=lambda folder: folder.pk)
    folders_dict = [{"name": folders_list[i].name, "parent_folder_id": folders_list[i].parent_folder.id}
                    for i in range(0, len(folders_list))]

    return JsonResponse(folders_dict, safe=False)


def post_folder(request):
    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)
    if not data["name"] or not data["parent_folder_id"]:
        return HttpResponseBadRequest()
    parent = Folder.objects.get(pk=data["parent_folder_id"])
    if not parent:
        return HttpResponseBadRequest()
    Folder.objects.create(name=data["name"], created=timezone.now(), parent_folder=parent)
    return HttpResponse("Created")


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
    return HttpResponse("Updated")


def delete_folder(request, id):
    folder = Folder.objects.get(pk=id)
    if folder:
        folder.delete()
        return HttpResponse("Ok")
    return HttpResponseNotFound()


def project_handler(request, id=None):
    if request.method == 'GET':
        if id:
            return get_project_json(request, id)
        return get_projects_json(request)
    elif request.method == 'POST':
        if id:
            return HttpResponseBadRequest()
        return post_project(request)
    elif request.method == 'PUT':
        return put_project(request, id)
    elif request.method == 'DELETE':
        return delete_project(request, id)
    return HttpResponseBadRequest()


def get_projects_json(request):
    projects_list = list(Project.objects.all())
    projects_list.sort(key=lambda project: project.pk)
    projects_dict = [{"name": projects_list[i].name, "folder": projects_list[i].folder.name}
                     for i in range(0, len(projects_list))]
    return JsonResponse(projects_dict, safe=False)


def get_project_json(request, id):
    project = Project.objects.get(pk=id)
    project_dict = {project.pk: {"name": project.name, "folder": project.folder.name}}
    return JsonResponse(project_dict)


def post_project(request):
    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)
    if not data["name"] or not data["parent_folder_id"]:
        return HttpResponseBadRequest()
    folder = Folder.objects.get(pk=data["parent_folder_id"])
    if not folder:
        return HttpResponseBadRequest()
    Project.objects.create(name=data["name"], created=timezone.now(), folder=folder)
    return HttpResponse("Created")


def put_project(request, id):
    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)
    project = Project.objects.get(pk=id)
    if not project:
        return HttpResponseNotFound()
    if data["name"]:
        project.name = data["name"]
    if data["parent_folder_id"]:
        folder = Folder.objects.get(pk=data["parent_folder_id"])
        if not folder:
            return HttpResponseBadRequest()
        project.folder = folder
    project.save()
    return HttpResponse("Updated")


def delete_project(request, id):
    project = Project.objects.get(pk=id)
    if project:
        project.delete()
        return HttpResponse("Ok")
    return HttpResponseNotFound()


@csrf_exempt
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


def get_document_json(request, id):
    document = Document.objects.get(pk=id)
    document_dict = {"id": document.id, "name": document.name, "type": document.type,
                     "size": document.size, "category": document.category, "section_id": document.section_id}
    return JsonResponse(document_dict)


def post_document(request):
    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)
    if not all (k in data for k in ("name","category","content","project_id")):
        return HttpResponseBadRequest(JsonResponse({"errors":"Fehler"}))
    project = Project.objects.get(pk=data["project_id"])
    if not project:
        return HttpResponseBadRequest()
    # temp demo code
    section = project.section_set.first()
    # /temp demo code
    binary_content = binascii.a2b_base64(data["content"])
    Document.objects.create(name=data["name"], type="pdf", size=1353653, status="None", category=data["category"],
                            content=binary_content, section=section)
    return HttpResponse("Created")


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
    return HttpResponse("Updated")


def delete_document(request, id):
    document = Document.objects.get(pk=id)
    if document:
        document.delete()
        return HttpResponse("Ok")
    return HttpResponseNotFound()


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


def get_requirement_json(request, id):
    requirement = Requirement.objects.get(pk=id)
    requirement_dict = {requirement.pk: {"id": requirement.id, "name": requirement.name,
                                         "values": [r.value for r in Requirement.objects.all() if r.name == requirement.name],
                                         "disabled": requirement.disabled}}
    return JsonResponse(requirement_dict)


def post_requirement(request):
    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)
    if not data["name"] or not data["values"] or not data["project_id"]:
        return HttpResponseBadRequest()
    project = Project.objects.get(pk=data["project_id"])
    if not project:
        return HttpResponseBadRequest()
    Requirement.objects.create(name=data["name"], values=data["values"], project=project)
    return HttpResponse("Created")


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
    return HttpResponse("Updated")


def delete_requirement(request, id):
    requirement = Requirement.objects.get(pk=id)
    if requirement:
        requirement.delete()
        return HttpResponse("Ok")
    return HttpResponseNotFound()


def get_requirements_of_project_json(request, id):
    requirements_list = list(Requirement.objects.filter(project_id=id))
    requirements_list.sort(key=lambda req: req.pk)
    requirements_dict = [{"id": requirements_list[i].id, "name": requirements_list[i].name,
                             "values": [r.value for r in requirements_list if r.name == requirements_list[i].name],
                             "document": requirements_list[i].document_id, "disabled": requirements_list[i].disabled}
                         for i in range(0, len(requirements_list))]
    return JsonResponse(requirements_dict, safe=False)


def get_documents_of_project_json(request, id):
    documents_list = list(Document.objects.filter(section__project_id=id))
    documents_list.sort(key=lambda doc: doc.pk)
    documents_dict = [{"id": documents_list[i].id, "name": documents_list[i].name,
                          "type": documents_list[i].type, "size": documents_list[i].size,
                          "status": documents_list[i].status, "category": documents_list[i].category,
                          "section_id": documents_list[i].section_id} for i in range(0, len(documents_list))]
    return JsonResponse(documents_dict, safe=False)


def mock_data():

    clear_db()
    print("Mocking Data")

    eu_comm_folder = Folder.objects.create(name="European Commission", parent_folder=None)
    Folder.objects.create(name="Deutsche Forschungsgemeinschaft", parent_folder=None)
    Folder.objects.create(name="Deutscher Akademischer Austauschdienst ", parent_folder=None)

    eu_leds_folder = Folder.objects.create(name="EU_LEDS", parent_folder=eu_comm_folder)
    eu_iot_folder = Folder.objects.create(name="EU_IOT", parent_folder=eu_comm_folder)

    user = User.objects.create(name="username", email="mail@mail.com")

    eu_leds2014_project = Project.objects.create(name="LEDS_2014", created=timezone.now(), folder=eu_leds_folder)
    eu_leds2016_project = Project.objects.create(name="LEDS_2016", created=timezone.now(), folder=eu_leds_folder)
    eu_iot_project = Project.objects.create(name="IOT_2010", created=timezone.now(), folder=eu_iot_folder)
    eu_h2020_project = Project.objects.create(name="H2020_2012", created=timezone.now(), folder=eu_comm_folder)

    eu_leds2014_section_general = Section.objects.create(name="General", project=eu_leds2014_project)
    eu_leds2014_call = Document.objects.create(name="Call.pdf", type="pdf", size=1353653, status="None", section=eu_leds2014_section_general, category='cal')
    eu_leds2014_template = Document.objects.create(name="Template.pdf", type="pdf", size=3786, status="None", section=eu_leds2014_section_general, category='tem')

    Requirement.objects.create(name="Title", value="Innovating SMEs", project=eu_leds2014_project, document=eu_leds2014_call)
    Requirement.objects.create(name="Deadline", value="30/07/2017", project=eu_leds2014_project, document=eu_leds2014_call)
    Requirement.objects.create(name="Project context", value="Horizon 2020", project=eu_leds2014_project, document=eu_leds2014_call)
    Requirement.objects.create(name="Project context", value="European Commission", project=eu_leds2014_project, document=eu_leds2014_call)
    Requirement.objects.create(name="Project context", value="Industrial Leadership", project=eu_leds2014_project, document=eu_leds2014_call)
    Requirement.objects.create(name="Length", value="60 pages", project=eu_leds2014_project, document=eu_leds2014_call)
    Requirement.objects.create(name="Participation Limitations", value="The participation of female members must be at least 30%", project=eu_leds2014_project, document=eu_leds2014_call)
    Requirement.objects.create(name="Participation Limitations", value="Consortium institutions must originate from 3 different EU countries", project=eu_leds2014_project, document=eu_leds2014_call)
    Requirement.objects.create(name="Scope", value="The above describes three intervowen aspects of a challenge to segment the (SME-)Clients of public innovation support in order to achieve a higher social return from the investments into ...", project=eu_leds2014_project, document=eu_leds2014_call)

    Membership.objects.create(user=user, project=eu_leds2014_project)
    Membership.objects.create(user=user, project=eu_iot_project)
    Membership.objects.create(user=user, project=eu_h2020_project)


def clear_db():

    print("Clearing DB")
    Document.objects.all().delete()
    ExternalPlatform.objects.all().delete()
    Folder.objects.all().delete()
    Membership.objects.all().delete()
    Project.objects.all().delete()
    Requirement.objects.all().delete()
    Section.objects.all().delete()
    User.objects.all().delete()

    try:
        db_connection = psycopg2.connect("dbname='hetdb' user='postgres' host='localhost' password='postgres'")
    except:
        print("I am unable to connect to the database")

    db_cursor = db_connection.cursor()
    
    db_cursor.execute("""ALTER SEQUENCE public.hetaddon_document_id_seq RESTART WITH 1""")
    db_cursor.execute("""ALTER SEQUENCE public.hetaddon_externalplatform_id_seq RESTART WITH 1""")
    db_cursor.execute("""ALTER SEQUENCE public.hetaddon_folder_id_seq RESTART WITH 1""")
    db_cursor.execute("""ALTER SEQUENCE public.hetaddon_membership_id_seq RESTART WITH 1""")
    db_cursor.execute("""ALTER SEQUENCE public.hetaddon_project_id_seq RESTART WITH 1""")
    db_cursor.execute("""ALTER SEQUENCE public.hetaddon_requirement_id_seq RESTART WITH 1""")
    db_cursor.execute("""ALTER SEQUENCE public.hetaddon_section_id_seq RESTART WITH 1""")
    db_cursor.execute("""ALTER SEQUENCE public.hetaddon_user_id_seq RESTART WITH 1""")



