from django.shortcuts import render
from .models import Folder, Project, User, Membership, Document, Requirement, DocumentCategory, Section
from django.utils import timezone
from django.http import HttpResponse

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

    print("Sending projects:")
    print(*user_projects_list, sep=', ')
    print("Sending folders:")
    print(*user_folders_list, sep=', ')

    return render(request, 'addon/index.html', context)

#fkn bad, pls rewrite after demo
def projects(request):
    folders = Folder.objects.all()
    result = "["
    for folder in folders:
        result += "{\"id\":42, \"name\":\"" + folder.name + "\", \"folders\": [], \"projects\": []},"
    result = result[0:-1]
    result += "]"
    return HttpResponse(result)

#fkn bad, pls rewrite after demo
def projectRequirements(request, id):
    requirements = Requirement.objects.all()
    result = "["
    for requirement in requirements:
        result += "{\"id\":42, \"name\":\"" + requirement.name + "\", \"value\":[\"" + requirement.value + "\"]},"
    result = result[0:-1]
    result += "]"
    return HttpResponse(result)

#fkn bad, pls rewrite after demo
def projectDocuments(request, id):
    documents = Document.objects.all()
    result = "["
    for document in documents:
        result += "{\"id\":42, \"name\":\"" + document.name + "\", \"type\":\"" + document.type + "\", \"size\":\"0.0\", \"category\":\"Test\"},"
    result = result[0:-1]
    result += "]"
    return HttpResponse(result)

def mock_data():

    clear_db()
    print("Mocking fake data into DB")

    eu_comm_folder = Folder.objects.create(name="European Commission", parent_folder=None)
    Folder.objects.create(name="Deutsche Forschungsgemeinschaft", parent_folder=None)
    Folder.objects.create(name="Deutscher Akademischer Austauschdienst ", parent_folder=None)

    user = User.objects.create(name="username", email="mail@mail.com")

    eu_leds_project = Project.objects.create(name="EU_LEDS_2014", created=timezone.now(), folder=eu_comm_folder)
    Project.objects.create(name="EU_IOT_2010", created=timezone.now(), folder=eu_comm_folder)
    Project.objects.create(name="EU_H2020_2012", created=timezone.now(), folder=eu_comm_folder)
    
    some_category = DocumentCategory.objects.create(name="Some Category")
    eu_leds_section_general = Section.objects.create(name="General", project=eu_leds_project)
    eu_leds_doc_call = Document.objects.create(name="Call.pdf", type="pdf", status="None", section=eu_leds_section_general, category=some_category)
    Requirement.objects.create(name="Title", value="Innovating SMEs", project=eu_leds_project, document=eu_leds_doc_call)

    # eu_leds_project.members.add(user)
    # eu_leds_project.save()

    return None


def clear_db():

    print("Clearing DB")
    Folder.objects.all().delete()
    Project.objects.all().delete()
    User.objects.all().delete()
    Document.objects.all().delete()
    Requirement.objects.all().delete()
    Section.objects.all().delete()
    DocumentCategory.objects.all().delete()



