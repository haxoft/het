from django.shortcuts import render
from .models import *
from django.utils import timezone
from django.http import *
from django.core import serializers
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


def get_folders_json(request):
    folders_list = list(Folder.objects.all())
    folders_list.sort(key=lambda folder: folder.pk)
    folders_dict = {i: {"name": folders_list[i].name, "parent_folder": folders_list[i].parent_folder}
                    for i in range(0, len(folders_list))}

    return JsonResponse(folders_dict, safe=False)


def project_handler(request):
    if request.method == 'GET':
        return get_projects_json(request)
    elif request.method == 'POST':
        return post_project(request)


def get_projects_json(request):
    projects_list = list(Project.objects.all())
    projects_list.sort(key=lambda project: project.pk)
    projects_dict = {i: {"name": projects_list[i].name, "folder": projects_list[i].folder.name}
                     for i in range(0, len(projects_list))}
    return JsonResponse(projects_dict)


def post_project(request):
    pass


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


def get_requirements_of_project_json(request, id):
    requirements_list = list(Requirement.objects.filter(project_id=id))
    requirements_list.sort(key=lambda req: req.pk)
    requirements_dict = {i: {'name': requirements_list[i].name, "value": requirements_list[i].value,
                             "document": requirements_list[i].document_id} for i in range(0, len(requirements_list))}
    return JsonResponse(requirements_dict)


def get_documents_of_project_json(request, id):
    documents_list = list(Requirement.objects.filter(project_id=id))
    documents_list.sort(key=lambda req: req.pk)
    documents_dict = {i: {'name': documents_list[i].name, "type": documents_list[i].type,
                          "status": documents_list[i].status, "category_id": documents_list[i].category_id,
                          "section": documents_list[i].section_id} for i in range(0, len(documents_list))}
    return JsonResponse(documents_dict)


def mock_data():

    clear_db()
    print("Mocking Data")

    root_folder = Folder.objects.create(name="Projects", parent_folder=None)
    eu_comm_folder = Folder.objects.create(name="European Commission", parent_folder=root_folder)
    Folder.objects.create(name="Deutsche Forschungsgemeinschaft", parent_folder=root_folder)
    Folder.objects.create(name="Deutscher Akademischer Austauschdienst ", parent_folder=root_folder)

    user = User.objects.create(name="username", email="mail@mail.com")

    eu_leds_project = Project.objects.create(name="EU_LEDS_2014", created=timezone.now(), folder=eu_comm_folder)
    eu_iot_project = Project.objects.create(name="EU_IOT_2010", created=timezone.now(), folder=eu_comm_folder)
    eu_h2020_project = Project.objects.create(name="EU_H2020_2012", created=timezone.now(), folder=eu_comm_folder)
    
    some_category = DocumentCategory.objects.create(name="Some Category")
    eu_leds_section_general = Section.objects.create(name="General", project=eu_leds_project)
    eu_leds_doc_call = Document.objects.create(name="Call.pdf", type="pdf", status="None", section=eu_leds_section_general, category=some_category)
    Requirement.objects.create(name="Title", value="Innovating SMEs", project=eu_leds_project, document=eu_leds_doc_call)

    Membership.objects.create(user=user, project=eu_leds_project)
    Membership.objects.create(user=user, project=eu_iot_project)
    Membership.objects.create(user=user, project=eu_h2020_project)


def clear_db():

    print("Clearing DB")
    Document.objects.all().delete()
    DocumentCategory.objects.all().delete()
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
    db_cursor.execute("""ALTER SEQUENCE public.hetaddon_documentcategory_id_seq RESTART WITH 1""")
    db_cursor.execute("""ALTER SEQUENCE public.hetaddon_externalplatform_id_seq RESTART WITH 1""")
    db_cursor.execute("""ALTER SEQUENCE public.hetaddon_folder_id_seq RESTART WITH 1""")
    db_cursor.execute("""ALTER SEQUENCE public.hetaddon_membership_id_seq RESTART WITH 1""")
    db_cursor.execute("""ALTER SEQUENCE public.hetaddon_project_id_seq RESTART WITH 1""")
    db_cursor.execute("""ALTER SEQUENCE public.hetaddon_requirement_id_seq RESTART WITH 1""")
    db_cursor.execute("""ALTER SEQUENCE public.hetaddon_section_id_seq RESTART WITH 1""")
    db_cursor.execute("""ALTER SEQUENCE public.hetaddon_user_id_seq RESTART WITH 1""")



