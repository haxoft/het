from datetime import timezone
from django.utils import timezone
from hetaddon.models.model import *
import psycopg2
import logging

log = logging.getLogger('django')


def mock_data():
    clear_db()
    log.info("Mocking Data")

    eu_comm_folder = Folder.objects.create(name="European Commission", parent_folder=None)
    Folder.objects.create(name="Deutsche Forschungsgemeinschaft", parent_folder=None)
    Folder.objects.create(name="Deutscher Akademischer Austauschdienst ", parent_folder=None)

    eu_leds_folder = Folder.objects.create(name="EU_LEDS", parent_folder=eu_comm_folder)
    eu_iot_folder = Folder.objects.create(name="EU_IOT", parent_folder=eu_comm_folder)

    user = User.objects.create(name="admin", email="mail@mail.com")
    ExternalPlatform.objects.create(platform_name='atl', user_ext_id='admin', user=user)

    eu_leds2014_project = Project.objects.create(name="LEDS_2014", created=timezone.now(), folder=eu_leds_folder)
    eu_leds2016_project = Project.objects.create(name="LEDS_2016", created=timezone.now(), folder=eu_leds_folder)
    eu_iot_project = Project.objects.create(name="IOT_2010", created=timezone.now(), folder=eu_iot_folder)
    eu_h2020_project = Project.objects.create(name="H2020_2012", created=timezone.now(), folder=eu_comm_folder)

    eu_leds2014_section_general = Section.objects.create(name="General", project=eu_leds2014_project)
    eu_leds2014_call = Document.objects.create(name="Call.pdf", type="pdf", size=1353653, status="None",
                                               section=eu_leds2014_section_general, category='cal')
    eu_leds2014_template = Document.objects.create(name="Template.pdf", type="pdf", size=3786, status="None",
                                                   section=eu_leds2014_section_general, category='tem')

    title_req = Requirement.objects.create(name="Title", project=eu_leds2014_project)
    RequirementValue.objects.create(value="Innovating SMEs", requirement=title_req, document=eu_leds2014_call)

    deadline_req = Requirement.objects.create(name="Deadline", project=eu_leds2014_project)
    RequirementValue.objects.create(value="30/07/2017", requirement=deadline_req, document=eu_leds2014_call)

    context_req = Requirement.objects.create(name="Project context", project=eu_leds2014_project)
    RequirementValue.objects.create(value="Horizon 2020", requirement=context_req, document=eu_leds2014_call)
    RequirementValue.objects.create(value="European Commission", requirement=context_req, document=eu_leds2014_call)
    RequirementValue.objects.create(value="Industrial Leadership", requirement=context_req, document=eu_leds2014_call)

    lenght_req = Requirement.objects.create(name="Length", project=eu_leds2014_project)
    RequirementValue.objects.create(value="60 pages", requirement=lenght_req, document=eu_leds2014_call)

    particip_req = Requirement.objects.create(name="Participation Limitations", project=eu_leds2014_project)
    RequirementValue.objects.create(value="The participation of female members must be at least 30%",
                                    requirement=particip_req, document=eu_leds2014_call)
    RequirementValue.objects.create(value="Consortium institutions must originate from 3 different EU countries",
                                    requirement=particip_req, document=eu_leds2014_call)

    scope_req = Requirement.objects.create(name="Scope", project=eu_leds2014_project)
    RequirementValue.objects.create(value="The above describes three intervowen aspects of a "
                                          "challenge to segment the (SME-)Clients of public innovation support in "
                                          "order to achieve a higher social return from the investments into ...",
                                    requirement=scope_req, document=eu_leds2014_call)

    Membership.objects.create(user=user, project=eu_leds2014_project)
    Membership.objects.create(user=user, project=eu_iot_project)
    Membership.objects.create(user=user, project=eu_h2020_project)


def clear_db():
    Document.objects.all().delete()
    ExternalPlatform.objects.all().delete()
    Folder.objects.all().delete()
    Membership.objects.all().delete()
    Project.objects.all().delete()
    Requirement.objects.all().delete()
    RequirementValue.objects.all().delete()
    Section.objects.all().delete()
    User.objects.all().delete()

    try:
        db_connection = psycopg2.connect("dbname='hetdb' user='postgres' host='localhost' password='postgres'")

        db_cursor = db_connection.cursor()

        db_cursor.execute("""ALTER SEQUENCE public.hetaddon_document_id_seq RESTART WITH 1""")
        db_cursor.execute("""ALTER SEQUENCE public.hetaddon_externalplatform_id_seq RESTART WITH 1""")
        db_cursor.execute("""ALTER SEQUENCE public.hetaddon_folder_id_seq RESTART WITH 1""")
        db_cursor.execute("""ALTER SEQUENCE public.hetaddon_membership_id_seq RESTART WITH 1""")
        db_cursor.execute("""ALTER SEQUENCE public.hetaddon_project_id_seq RESTART WITH 1""")
        db_cursor.execute("""ALTER SEQUENCE public.hetaddon_requirement_id_seq RESTART WITH 1""")
        db_cursor.execute("""ALTER SEQUENCE public.hetaddon_requirementvalue_id_seq RESTART WITH 1""")
        db_cursor.execute("""ALTER SEQUENCE public.hetaddon_section_id_seq RESTART WITH 1""")
        db_cursor.execute("""ALTER SEQUENCE public.hetaddon_user_id_seq RESTART WITH 1""")
    except:
        print("I am unable to connect to the database")

