from django.test import TestCase
from django.utils import timezone

from hetaddon.models.model import *
import json


class FolderViews(TestCase):

    """ Test that all folders are retrieved with their corresponding structure """

    def test_get_folders_structure(self):

        resp = self.client.get('/hxt/api/folders')
        self.assertEquals(resp.status_code, 401)  # unauthorized

        user = self.mock_user_session()

        root_folder_1 = RootFolder.objects.create(name="root_folder_1", parent_folder=None, owner=user)
        root_folder_2 = RootFolder.objects.create(name="root_folder_2", parent_folder=None, owner=user)
        folder_1a = Folder.objects.create(name="folder_1a", parent_folder=root_folder_1)
        folder_1b = Folder.objects.create(name="folder_1b", parent_folder=root_folder_1)
        folder_2a = Folder.objects.create(name="folder_2a", parent_folder=root_folder_2)

        folders_list = list(Folder.objects.all())
        self.assertTrue(len(folders_list) == 5)

        resp = self.client.get('/hxt/api/folders')
        self.assertEquals(resp.status_code, 200)
        self.assertTrue(type(resp.json()) is list)
        self.assertJSONEqual(
            str(resp.content, encoding='utf8'),
            [{"id": root_folder_1.id, "name": root_folder_1.name,
                "folders": [
                    {"id": folder_1b.id, "name": folder_1b.name, "folders": [], "projects": []},
                    {"id": folder_1a.id, "name": folder_1a.name, "folders": [], "projects": []}
                ],
                "projects": []},
            {"id": root_folder_2.id, "name": root_folder_2.name,
                "folders": [
                        {"id": folder_2a.id, "name": folder_2a.name, "folders": [], "projects": []}],
                "projects": []}]
        )

    """ Test that all folders are retrieved with their corresponding structure, including projects (if any) """

    def test_get_folders_structure_with_projects(self):

        resp = self.client.get('/hxt/api/folders')
        self.assertEquals(resp.status_code, 401)  # unauthorized

        user = self.mock_user_session()

        root_folder_1 = RootFolder.objects.create(name="root_folder_1", parent_folder=None, owner=user)
        root_folder_2 = RootFolder.objects.create(name="root_folder_2", parent_folder=None, owner=user)
        folder_1a = Folder.objects.create(name="folder_1a", parent_folder=root_folder_1)
        folder_1b = Folder.objects.create(name="folder_1b", parent_folder=root_folder_1)
        folder_2a = Folder.objects.create(name="folder_2a", parent_folder=root_folder_2)
        proj_1a = Project.objects.create(name="project_1a", created=timezone.now())
        proj_1b = Project.objects.create(name="project_1b", created=timezone.now())
        ProjectFolder.objects.create(project=proj_1a, folder=folder_1a)
        ProjectFolder.objects.create(project=proj_1b, folder=folder_1b)

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
                {"id": root_folder_1.id, "name": root_folder_1.name,
                    "folders": [
                        {"id": folder_1b.id, "name": folder_1b.name, "folders": [], "projects":
                            [{"id": proj_1b.id, "name": proj_1b.name, "requirementsExtracted": False}]},
                        {"id": folder_1a.id, "name": folder_1a.name, "folders": [], "projects":
                            [{"id": proj_1a.id, "name": proj_1a.name, "requirementsExtracted": False}]}],
                    "projects": []},
                {"id": root_folder_2.id, "name": root_folder_2.name,
                    "folders": [
                        {"id": folder_2a.id, "name": folder_2a.name, "folders": [], "projects": []}],
                    "projects": []}]
        )

    """ Test that a sub-folder is correctly created """

    def test_create_folder(self):

        resp = self.client.post('/hxt/api/folders', json.dumps({}), content_type="application/json")
        self.assertEquals(resp.status_code, 401)  # unauthorized

        user = self.mock_user_session()

        root_folder = RootFolder.objects.create(name="parent_folder", parent_folder=None, owner=user)
        folders_list = list(Folder.objects.all())
        self.assertTrue(len(folders_list) == 1)
        test_folder_dict = {'name': 'folder_name', 'parent_folder_id': str(root_folder.id)}

        resp = self.client.post('/hxt/api/folders', json.dumps(test_folder_dict), content_type="application/json")
        self.assertEquals(resp.status_code, 201)
        folders_list = list(Folder.objects.all())
        self.assertTrue(len(folders_list) == 2)

    """ Test that creating a sub-folder with a parent that doesnt belong to the requesting user is not created """

    def test_create_folder_foreign_parent(self):

        resp = self.client.post('/hxt/api/folders', json.dumps({}), content_type="application/json")
        self.assertEquals(resp.status_code, 401)  # unauthorized

        user = self.mock_user_session()
        second_user = User.objects.create(name="user2", email="mail@mail.de")

        root_folder = RootFolder.objects.create(name="root_folder", parent_folder=None, owner=second_user)
        folders_list = list(Folder.objects.all())
        self.assertTrue(len(folders_list) == 1)
        test_folder_dict = {'name': 'folder_name', 'parent_folder_id': str(root_folder.id)}

        resp = self.client.post('/hxt/api/folders', json.dumps(test_folder_dict), content_type="application/json")
        self.assertEquals(resp.status_code, 401)
        self.assertEquals(resp.content.decode('utf-8'),
                          "Unauthorized! Parent folder [" + str(root_folder.id) + "] is not yours!")
        folders_list = list(Folder.objects.all())
        self.assertTrue(len(folders_list) == 1)

    """ Test that a root folder is correctly created """

    def test_create_root_folder(self):

        resp = self.client.post('/hxt/api/folders', json.dumps({}), content_type="application/json")
        self.assertEquals(resp.status_code, 401)  # unauthorized

        user = self.mock_user_session()

        folders_list = list(Folder.objects.all())
        self.assertTrue(len(folders_list) == 0)
        test_root_folder_dict = {'name': 'folder_name', 'parent_folder_id': None}
        resp = self.client.post('/hxt/api/folders', json.dumps(test_root_folder_dict), content_type="application/json")
        self.assertEquals(resp.status_code, 201)
        folders_list = list(Folder.objects.all())
        self.assertTrue(len(folders_list) == 1)
        self.assertEquals(user, folders_list[0].rootfolder.owner)

        """ Test that an error is returned on missing required name parameter """
        resp = self.client.post('/hxt/api/folders', json.dumps({'name': '', 'parent_folder_id': ''}),
                                content_type="application/json")
        self.assertEquals(resp.content.decode('utf-8'), 'Found empty required parameter: name')
        self.assertEquals(resp.status_code, 400)
        folders_list = list(Folder.objects.all())
        self.assertTrue(len(folders_list) == 1)

    """ Test that a folder is correctly updated """

    def test_update_folder(self):

        resp = self.client.put('/hxt/api/folders', json.dumps({}), content_type="application/json")
        self.assertEquals(resp.status_code, 401)  # unauthorized

        user = self.mock_user_session()

        test_root_folder = RootFolder.objects.create(name="parent_folder", parent_folder=None, owner=user)
        test_folder = Folder.objects.create(name="test_folder", parent_folder=None)

        folders_list = list(Folder.objects.all())
        self.assertTrue(len(folders_list) == 2)
        folder_update = {'name': 'updated_name', 'parent_folder_id': str(test_root_folder.id)}

        resp = self.client.put('/hxt/api/folders/' + str(test_folder.id), json.dumps(folder_update),
                               content_type="application/json")
        self.assertEquals(resp.status_code, 200)
        updated_folder = Folder.objects.get(pk=test_folder.id)
        self.assertEquals(updated_folder.name, folder_update['name'])
        self.assertEquals(str(updated_folder.parent_folder.id), folder_update['parent_folder_id'])

    """ Test that a folder is correctly deleted """

    def test_delete_folder(self):

        resp = self.client.delete('/hxt/api/folders', json.dumps({}), content_type="application/json")
        self.assertEquals(resp.status_code, 401)  # unauthorized

        user = self.mock_user_session()

        test_root_folder = RootFolder.objects.create(name="root", parent_folder=None, owner=user)
        test_folder = Folder.objects.create(name="EU_LEDS", parent_folder=test_root_folder)
        folders_list = list(Folder.objects.all())
        self.assertTrue(len(folders_list) == 2)

        resp = self.client.delete('/hxt/api/folders/' + str(test_folder.id))
        self.assertEquals(resp.content.decode('utf-8'), 'Deleted folder ' + str(test_folder.id))
        print("Received msg:" + resp.content.decode('utf-8'))
        self.assertEquals(resp.status_code, 200)
        folders_list = list(Folder.objects.all())
        self.assertTrue(len(folders_list) == 1)

    """ Test that a ROOT folder is correctly deleted """

    def test_delete_folder(self):

        resp = self.client.delete('/hxt/api/folders', json.dumps({}), content_type="application/json")
        self.assertEquals(resp.status_code, 401)  # unauthorized

        user = self.mock_user_session()

        test_root_folder = RootFolder.objects.create(name="root", parent_folder=None, owner=user)
        folders_list = list(Folder.objects.all())
        self.assertTrue(len(folders_list) == 1)

        resp = self.client.delete('/hxt/api/folders/' + str(test_root_folder.id))
        self.assertEquals(resp.content.decode('utf-8'), 'Deleted folder ' + str(test_root_folder.id))
        # print("Received msg:" + resp.content.decode('utf-8'))
        self.assertEquals(resp.status_code, 200)
        folders_list = list(Folder.objects.all())
        self.assertTrue(len(folders_list) == 0)

    def mock_user_session(self):

        user_ext_id = 'admin'
        user = User.objects.create(name="admin", email="mail@mail.com")
        ExternalPlatform.objects.create(platform_name='atl', user_ext_id=user_ext_id, user=user)

        session = self.client.session
        session['user'] = {'userKey': user_ext_id}
        session.save()
        return user

