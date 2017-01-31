from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import *


class IndexView(TestCase):

    """ Testing if the index view is available on equivalent URLs """

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/hxt/')
        self.assertEqual(response.status_code, 200)


class ProjectViews(TestCase):

    """ Test that all projects are retrieved and JSON is returned in the correct format """

    def test_get_all_projects(self):

        eu_leds_folder = Folder.objects.create(name="EU_LEDS", parent_folder=None)
        leds_project = Project.objects.create(name="LEDS_2014", created=timezone.now(), folder=eu_leds_folder)

        response = self.client.get('/hxt/api/projects')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(type(response.json()) is list)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            [{'name': leds_project.name, 'folder': eu_leds_folder.name}]
        )

        Project.objects.create(name="Test_project", created=timezone.now(), folder=eu_leds_folder)
        response = self.client.get('/hxt/api/projects')
        self.assertEqual(response.status_code, 200)
        projs_list = response.json()
        self.assertTrue(type(projs_list) is list)
        self.assertEquals(len(projs_list), 2)

    """ Test if a project is correctly retrieved byt its ID """

    def test_get_project_by_id(self):

        eu_leds_folder = Folder.objects.create(name="EU_LEDS", parent_folder=None)
        leds_project = Project.objects.create(name="LEDS_2014", created=timezone.now(), folder=eu_leds_folder)
        iot_project = Project.objects.create(name="IOT_2014", created=timezone.now(), folder=eu_leds_folder)

        response = self.client.get('/hxt/api/projects/' + str(leds_project.id))
        self.assertEqual(response.status_code, 200)
        leds_dict = response.json()
        self.assertTrue(type(leds_dict) is dict)
        self.assertEqual(leds_dict,
                         {'name': leds_project.name, 'folder': leds_project.folder.name})

        response = self.client.get('/hxt/api/projects/' + str(iot_project.id))
        self.assertEqual(response.status_code, 200)
        iot_dict = response.json()
        self.assertTrue(type(iot_dict) is dict)
        self.assertEqual(iot_dict,
                         {'name': iot_project.name, 'folder': iot_project.folder.name})

    """ Test if a project is correctly created """

    def test_create_project(self):

        eu_leds_folder = Folder.objects.create(name="EU_LEDS", parent_folder=None)
        # leds_project = Project.objects.create(name="LEDS_2014", created=timezone.now(), folder=eu_leds_folder)
        # iot_project = Project.objects.create(name="IOT_2014", created=timezone.now(), folder=eu_leds_folder)

        projs_list = list(Project.objects.all())
        self.assertTrue(len(projs_list) == 0)
        test_proj_dict = {'name': 'ttest_project', 'parent_folder_id': str(eu_leds_folder.id)}
        resp = self.client.post('/hxt/api/projects', test_proj_dict)
        print(resp)
        self.assertEquals(resp.status_code, 200)

        # projs_list = list(Project.objects.all())
        # print(len(projs_list))
        # self.assertTrue()



