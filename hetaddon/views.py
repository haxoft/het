from django.shortcuts import render
from .models import Folder, Project, User, Membership
from django.utils import timezone

#  nasty, remove
mocked = False


def index(request):

    # mock per backend run
    global mocked
    if not mocked:
        mock_data()
        mocked = True

    # ...some user retrieval using jwt
    userId = 1
    user_folders_list = Folder.objects.all()  # ... getting folders for a specific user might be tricky
    user_projects_list = Project.objects.all()

    context = {
        'folders': user_folders_list,
        'projects:': user_projects_list,
    }

    return render(request, 'addon/index.html', context)


def mock_data():

    clear_db()
    print("Mocking fake data into DB")

    root_folder = Folder(name="Projects", parent_folder=None)
    root_folder.save()
    eu_comm_folder = Folder(name="European Commission", parent_folder=root_folder)
    eu_comm_folder.save()
    dfg_folder = Folder(name="Deutsche Forschungsgemeinschaft", parent_folder=root_folder)
    dfg_folder.save()
    daf_folder = Folder(name="Deutscher Akademischer Austauschdienst ", parent_folder=root_folder)
    daf_folder.save()

    user = User(name="username", email="mail@mail.com")
    user.save()

    eu_leds_project = Project(name="EU_LEDS_2014", created=timezone.now(), folder=eu_comm_folder)
    eu_leds_project.save()

    eu_iot_project = Project(name="EU_IOT_2010", created=timezone.now(), folder=eu_comm_folder)
    eu_iot_project.save()

    eu_2020_project = Project(name="EU_H2020_2012", created=timezone.now(), folder=eu_comm_folder)
    eu_2020_project.save()


    # eu_leds_project.members.add(user)
    # eu_leds_project.save()

    return None


def clear_db():

    print("Clearing DB")
    Folder.objects.all().delete()
    Project.objects.all().delete()
    User.objects.all().delete()



