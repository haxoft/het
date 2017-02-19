from django.test import TestCase
from django.utils import timezone

from hetaddon.models.model import *
import json


class ProjectViews(TestCase):

    """ Test that all projects are retrieved and JSON is returned in the correct format """

    def test_get_all_projects(self):

        eu_leds_folder = Folder.objects.create(name="EU_LEDS", parent_folder=None)
        leds_project = Project.objects.create(name="LEDS_2014", created=timezone.now(), folder=eu_leds_folder)
        test_project = Project.objects.create(name="Test_project", created=timezone.now(), folder=eu_leds_folder)

        response = self.client.get('/hxt/api/projects')
        self.assertEqual(response.status_code, 200)

        projects_list = response.json()
        self.assertTrue(isinstance(projects_list, list))
        self.assertTrue(len(projects_list) == 2)

        self.assertEquals(projects_list[0]["name"], leds_project.name)
        self.assertEquals(projects_list[0]["folder_id"], leds_project.folder.id)
        self.assertEquals(projects_list[1]["name"], test_project.name)
        self.assertEquals(projects_list[1]["folder_id"], test_project.folder.id)

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

    """ Test that a project is correctly created """

    def test_create_project(self):

        eu_leds_folder = Folder.objects.create(name="EU_LEDS", parent_folder=None)

        projs_list = list(Project.objects.all())
        self.assertTrue(len(projs_list) == 0)
        test_proj_dict = {'name': 'ttest_project', 'parent_folder_id': str(eu_leds_folder.id)}

        resp = self.client.post('/hxt/api/projects', json.dumps(test_proj_dict), content_type="application/json")
        self.assertEquals(resp.status_code, 201)
        projs_list = list(Project.objects.all())
        self.assertTrue(len(projs_list) == 1)

        """ Test that an error is returned on missing data """
        resp = self.client.post('/hxt/api/projects', json.dumps({'name': 'name', 'parent_folder_id': ''}),
                                content_type="application/json")
        self.assertEquals(resp.status_code, 400)
        self.assertEquals(resp.content.decode('utf-8'),
                          "Found empty required parameters! 'Name' or 'parent_folder_id' fields are missing")

    """ Test that a project is correctly updated """

    def test_update_project(self):

        test_folder = Folder.objects.create(name="test_folder", parent_folder=None)
        test_project = Project.objects.create(name="test_project", created=timezone.now(), folder=test_folder)

        projs_list = list(Project.objects.all())
        self.assertTrue(len(projs_list) == 1)
        proj_update = {'name': 'updated_name', 'parent_folder_id': str(test_folder.id)}

        resp = self.client.put('/hxt/api/projects/' + str(test_project.id), json.dumps(proj_update),
                               content_type="application/json")
        self.assertEquals(resp.status_code, 200)

        updated_proj = Project.objects.get(pk=test_project.id)
        self.assertEquals(updated_proj.name, proj_update['name'])
        self.assertEquals(str(updated_proj.folder.id), proj_update['parent_folder_id'])

        """ Test that an error is returned on non-existing parent folder ID """

        proj_update = {'name': '', 'parent_folder_id': 555}
        resp = self.client.put('/hxt/api/projects/' + str(test_project.id), json.dumps(proj_update),
                               content_type="application/json")
        self.assertEquals(resp.status_code, 404)

    """ Test that a project is correctly deleted """

    def test_delete_project(self):

        eu_leds_folder = Folder.objects.create(name="EU_LEDS", parent_folder=None)
        leds_project = Project.objects.create(name="LEDS_2014", created=timezone.now(), folder=eu_leds_folder)

        projs_list = list(Project.objects.all())
        self.assertTrue(len(projs_list) == 1)

        resp = self.client.delete('/hxt/api/projects/' + str(leds_project.id))
        self.assertEquals(resp.status_code, 200)
        projs_list = list(Project.objects.all())
        self.assertTrue(len(projs_list) == 0)