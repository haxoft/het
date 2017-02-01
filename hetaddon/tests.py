from binascii import a2b_base64

from django.test import TestCase
from django.test import TransactionTestCase
from django.urls import reverse
from django.utils import timezone
import base64

from .models import *
import json


class IndexView(TestCase):

    """ Test the index view page rendering """

    """ Test that the index view is available on equivalent URLs """

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

        eu_leds_folder = Folder.objects.create(name="EU_LEDS", parent_folder=None)
        leds_project = Project.objects.create(name="LEDS_2014", created=timezone.now(), folder=eu_leds_folder)

        projs_list = list(Project.objects.all())
        self.assertTrue(len(projs_list) == 1)
        proj_update = {'name': 'updated_name', 'parent_folder_id': str(eu_leds_folder.id)}

        resp = self.client.put('/hxt/api/projects/' + str(leds_project.id), json.dumps(proj_update), content_type="application/json")
        self.assertEquals(resp.status_code, 200)
        updated_proj = Project.objects.get(pk=leds_project.id)
        self.assertEquals(updated_proj.name, proj_update['name'])
        self.assertEquals(str(updated_proj.folder.id), proj_update['parent_folder_id'])

        """ Test that an error is returned on missing data """

        proj_update = {'name': '', 'parent_folder_id': ''}
        resp = self.client.put('/hxt/api/projects/' + str(leds_project.id), json.dumps(proj_update),
                               content_type="application/json")
        self.assertEquals(resp.status_code, 400)
        self.assertEquals(resp.content.decode('utf-8'), "Found empty name and parent folder ID! NOP")

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


class FolderViews(TransactionTestCase):

    reset_sequences = True

    """ Test that all folders are retrieved with their corresponding structure """

    def test_get_folders_structure(self):

        top_folder_1 = Folder.objects.create(name="top_folder_1", parent_folder=None)
        top_folder_2 = Folder.objects.create(name="top_folder_2", parent_folder=None)
        folder_1a = Folder.objects.create(name="folder_1a", parent_folder=top_folder_1)
        folder_1b = Folder.objects.create(name="folder_1b", parent_folder=top_folder_1)
        folder_2a = Folder.objects.create(name="folder_2a", parent_folder=top_folder_2)

        folders_list = list(Folder.objects.all())
        self.assertTrue(len(folders_list) == 5)

        resp = self.client.get('/hxt/api/folders')
        self.assertEquals(resp.status_code, 200)
        self.assertTrue(type(resp.json()) is list)
        self.assertJSONEqual(
            str(resp.content, encoding='utf8'),
            [{"id": 1, "name": "top_folder_1",
                "folders": [
                    {"id": 4, "name": "folder_1b", "folders": [], "projects": []},
                    {"id": 3, "name": "folder_1a", "folders": [], "projects": []}
                ],
                "projects": []},
            {"id": 2, "name": "top_folder_2",
                "folders": [
                        {"id": 5, "name": "folder_2a", "folders": [], "projects": []}],
                "projects": []}]
        )

    """ Test that all folders are retrieved with their corresponding structure, including projects (if any) """

    def test_get_folders_structure_with_projects(self):

        top_folder_1 = Folder.objects.create(name="top_folder_1", parent_folder=None)
        top_folder_2 = Folder.objects.create(name="top_folder_2", parent_folder=None)
        folder_1a = Folder.objects.create(name="folder_1a", parent_folder=top_folder_1)
        folder_1b = Folder.objects.create(name="folder_1b", parent_folder=top_folder_1)
        Folder.objects.create(name="folder_2a", parent_folder=top_folder_2)
        Project.objects.create(name="project_1a", created=timezone.now(), folder=folder_1a)
        Project.objects.create(name="project_1b", created=timezone.now(), folder=folder_1b)

        folders_list = list(Folder.objects.all())
        self.assertTrue(len(folders_list) == 5)
        projects_list = list(Project.objects.all())
        self.assertTrue(len(projects_list) == 2)

        resp = self.client.get('/hxt/api/folders')
        self.assertEquals(resp.status_code, 200)
        self.assertTrue(type(resp.json()) is list)
        self.assertJSONEqual(
            str(resp.content, encoding='utf8'),
            [
                {"id": 1, "name": "top_folder_1",
                    "folders": [
                        {"id": 4, "name": "folder_1b", "folders": [], "projects":
                            [{"id": 2, "name": "project_1b", "requirementsExtracted": False}]},
                        {"id": 3, "name": "folder_1a", "folders": [], "projects":
                            [{"id": 1, "name": "project_1a", "requirementsExtracted": False}]}],
                    "projects": []},
                {"id": 2, "name": "top_folder_2",
                    "folders": [
                        {"id": 5, "name": "folder_2a", "folders": [], "projects": []}],
                    "projects": []}]
        )

    """ Test that a folder is correctly created """

    def test_create_folder(self):

        parent_folder = Folder.objects.create(name="parent_folder", parent_folder=None)
        folders_list = list(Folder.objects.all())
        self.assertTrue(len(folders_list) == 1)
        test_folder_dict = {'name': 'folder_name', 'parent_folder_id': str(parent_folder.id)}

        resp = self.client.post('/hxt/api/folders', json.dumps(test_folder_dict), content_type="application/json")
        self.assertEquals(resp.status_code, 201)
        folders_list = list(Folder.objects.all())
        self.assertTrue(len(folders_list) == 2)

    """ Test that a root folder (with no parent) is correctly created """

    def test_create_root_folder(self):

        folders_list = list(Folder.objects.all())
        self.assertTrue(len(folders_list) == 0)
        test_folder_dict = {'name': 'folder_name', 'parent_folder_id': None}

        resp = self.client.post('/hxt/api/folders', json.dumps(test_folder_dict), content_type="application/json")
        self.assertEquals(resp.status_code, 201)
        folders_list = list(Folder.objects.all())
        self.assertTrue(len(folders_list) == 1)

        """ Test that an error is returned on missing required name parameter """
        resp = self.client.post('/hxt/api/folders', json.dumps({'name': '', 'parent_folder_id': ''}),
                                content_type="application/json")
        self.assertEquals(resp.content.decode('utf-8'), 'Found empty required parameter: name')
        self.assertEquals(resp.status_code, 400)
        folders_list = list(Folder.objects.all())
        self.assertTrue(len(folders_list) == 1)

    """ Test that a folder is correctly updated """

    def test_update_folder(self):

        test_parent_folder = Folder.objects.create(name="parent_folder", parent_folder=None)
        test_folder = Folder.objects.create(name="test_folder", parent_folder=None)

        folders_list = list(Folder.objects.all())
        self.assertTrue(len(folders_list) == 2)
        folder_update = {'name': 'updated_name', 'parent_folder_id': str(test_parent_folder.id)}

        resp = self.client.put('/hxt/api/folders/' + str(test_folder.id), json.dumps(folder_update),
                               content_type="application/json")
        self.assertEquals(resp.status_code, 200)
        updated_folder = Folder.objects.get(pk=test_folder.id)
        self.assertEquals(updated_folder.name, folder_update['name'])
        self.assertEquals(str(updated_folder.parent_folder.id), folder_update['parent_folder_id'])

    """ Test that a folder is correctly deleted """

    def test_delete_folder(self):

        test_folder = Folder.objects.create(name="EU_LEDS", parent_folder=None)
        folders_list = list(Folder.objects.all())
        self.assertTrue(len(folders_list) == 1)

        resp = self.client.delete('/hxt/api/folders/' + str(test_folder.id))
        self.assertEquals(resp.status_code, 200)
        folders_list = list(Folder.objects.all())
        self.assertTrue(len(folders_list) == 0)


class DocumentViews(TestCase):

    """ Test that a document is correctly retrieved, given an ID """

    def test_get_document_by_id(self):

        test_folder = Folder.objects.create(name="EU_LEDS", parent_folder=None)
        test_project= Project.objects.create(name="test_project", created=timezone.now(), folder=test_folder)
        test_section = Section.objects.create(name="test_section", project=test_project)
        test_doc = Document.objects.create(name="test_doc", type="pdf", size=1353653, status="None",
                                           section=test_section, category='cal')

        response = self.client.get('/hxt/api/documents/' + str(test_doc.id))
        self.assertEqual(response.status_code, 200)
        doc_dict = response.json()
        self.assertTrue(type(doc_dict) is dict)
        self.assertEqual(doc_dict,
                         {'id': test_doc.id, 'category': test_doc.category, 'name': test_doc.name,
                          'section_id': test_doc.section_id, 'size': test_doc.size, 'type': test_doc.type})

    """ Test that a document is correctly created """

    def test_create_document(self):

        test_folder = Folder.objects.create(name="EU_LEDS", parent_folder=None)
        test_project = Project.objects.create(name="test_project", created=timezone.now(), folder=test_folder)
        test_section = Section.objects.create(name="test_section", project=test_project)

        doc_list = list(Document.objects.all())
        self.assertTrue(len(doc_list) == 0)

        bin_doc_content = base64.b64encode(bytes('data to be encoded', "utf-8"))
        print("bin content:" + str(bin_doc_content))
        test_doc_dict = {'name': 'test_doc', 'type': 'pdf', 'size': 1111111, 'section_id': test_section.id,
                         'category': 'cal', 'content': bin_doc_content.decode('utf-8')}

        resp = self.client.post('/hxt/api/documents', json.dumps(test_doc_dict), content_type="application/json")
        self.assertEquals(resp.status_code, 201)
        doc_list = list(Document.objects.all())
        self.assertTrue(len(doc_list) == 1)

        # TODO: test that the binary content is being correctly stored (i was unable to retrieve it back)

        """ Test that an error is returned on missing data """
        resp = self.client.post('/hxt/api/documents', json.dumps({'name': 'name', 'section_id': ''}),
                                content_type="application/json")
        self.assertEquals(resp.status_code, 400)
        self.assertEquals(resp.content.decode('utf-8'),
                          "Unexpected structure! Missing required parameters")

    """ Test that a document is correctly updated """

    def test_update_document(self):

        test_folder = Folder.objects.create(name="test_folder", parent_folder=None)
        test_project = Project.objects.create(name="test_project", created=timezone.now(), folder=test_folder)
        test_section = Section.objects.create(name="test_section", project=test_project)
        test_doc = Document.objects.create(name="test_doc", type="pdf", size=111111, status="None",
                                           section=test_section, category='cal')

        docs_list = list(Document.objects.all())
        self.assertTrue(len(docs_list) == 1)

        # if data["name"]:
        #     document.name = data["name"]
        # if data["type"]:
        #     document.type = data["type"]
        # if data["size"]:
        #     document.size = data["size"]
        # if data["category"]:
        #     document.category = data["category"]
        # if data["section_id"]:

        doc_update = {'name': 'updated_name', 'type': '', 'size': '', 'category': '', 'section_id': ''}

        resp = self.client.put('/hxt/api/documents/' + str(test_doc.id), json.dumps(doc_update),
                               content_type="application/json")
        self.assertEquals(resp.status_code, 200)
        updated_doc = Document.objects.get(pk=test_doc.id)
        self.assertEquals(updated_doc.name, doc_update['name'])

        # """ Test that an error is returned on missing data """
        #
        # proj_update = {'name': '', 'parent_folder_id': ''}
        # resp = self.client.put('/hxt/api/projects/' + str(leds_project.id), json.dumps(proj_update),
        #                        content_type="application/json")
        # self.assertEquals(resp.status_code, 400)
        # self.assertEquals(resp.content.decode('utf-8'), "Found empty name and parent folder ID! NOP")

    # """ Test that a project is correctly deleted """
    #
    # def test_delete_project(self):
    #
    #     eu_leds_folder = Folder.objects.create(name="EU_LEDS", parent_folder=None)
    #     leds_project = Project.objects.create(name="LEDS_2014", created=timezone.now(), folder=eu_leds_folder)
    #
    #     projs_list = list(Project.objects.all())
    #     self.assertTrue(len(projs_list) == 1)
    #
    #     resp = self.client.delete('/hxt/api/projects/' + str(leds_project.id))
    #     self.assertEquals(resp.status_code, 200)
    #     projs_list = list(Project.objects.all())
    #     self.assertTrue(len(projs_list) == 0)

