import logging
from django.test import TestCase
from django.utils import timezone
from hetaddon.views import utils
from hetaddon.models.model import *
import json

log = logging.getLogger('django')


class ProjectViews(TestCase):

    """ Test that all projects belonging to a user are retrieved and JSON is returned in the correct format """

    def test_get_all_projects(self):

        resp = self.client.get('/hxt/api/projects')
        self.assertEquals(resp.status_code, 401)  # unauthorized

        user = self.mock_user_session()
        test_user = User.objects.create(name="test_user", email="a@a.com")

        root_folder = RootFolder.objects.create(name="root_folder", parent_folder=None, owner=user)
        subfolder_a = Folder.objects.create(name="subfolder_a", parent_folder=root_folder)
        subfolder_b = Folder.objects.create(name="subfolder_b", parent_folder=root_folder)
        foreign_folder = RootFolder.objects.create(name="foreign_folder", parent_folder=None, owner=test_user)

        project_a = Project.objects.create(name="project_a", created=timezone.now())
        project_b = Project.objects.create(name="project_b", created=timezone.now())
        foreign_project = Project.objects.create(name="foreign_project", created=timezone.now())

        ProjectFolder.objects.create(project=project_a, folder=subfolder_a)
        ProjectFolder.objects.create(project=project_b, folder=subfolder_b)
        ProjectFolder.objects.create(project=foreign_project, folder=foreign_folder)

        Membership.objects.create(user=user, project=project_a)
        Membership.objects.create(user=user, project=project_b)
        Membership.objects.create(user=test_user, project=foreign_project)

        response = self.client.get('/hxt/api/projects')
        self.assertEqual(response.status_code, 200)

        projects_list = response.json()
        self.assertTrue(isinstance(projects_list, list))
        self.assertTrue(len(projects_list) == 2)
        log.debug("received:" + str(projects_list))
        self.assertEquals(projects_list[0]["name"], project_a.name)
        self.assertEquals(projects_list[0]["folder_id"], subfolder_a.id)
        self.assertEquals(projects_list[1]["name"], project_b.name)
        self.assertEquals(projects_list[1]["folder_id"], subfolder_b.id)

    """ Test if a project of a given user is correctly retrieved byt its ID """

    def test_get_project_by_id(self):

        resp = self.client.get('/hxt/api/projects')
        self.assertEquals(resp.status_code, 401)  # unauthorized

        user = self.mock_user_session()
        test_user = User.objects.create(name="test_user", email="a@a.com")

        root_folder = RootFolder.objects.create(name="root_folder", parent_folder=None, owner=user)
        subfolder_a = Folder.objects.create(name="subfolder_a", parent_folder=root_folder)
        subfolder_b = Folder.objects.create(name="subfolder_b", parent_folder=root_folder)
        foreign_folder = RootFolder.objects.create(name="foreign_folder", parent_folder=None, owner=test_user)

        project_a = Project.objects.create(name="project_a", created=timezone.now())
        project_b = Project.objects.create(name="project_b", created=timezone.now())
        foreign_project = Project.objects.create(name="foreign_project", created=timezone.now())

        ProjectFolder.objects.create(project=project_a, folder=subfolder_a)
        ProjectFolder.objects.create(project=project_b, folder=subfolder_b)
        ProjectFolder.objects.create(project=foreign_project, folder=foreign_folder)

        Membership.objects.create(user=user, project=project_a)
        Membership.objects.create(user=user, project=project_b)
        Membership.objects.create(user=test_user, project=foreign_project)

        response = self.client.get('/hxt/api/projects/' + str(project_a.id))
        self.assertEqual(response.status_code, 200)
        project_a_dict = response.json()
        self.assertEqual(project_a_dict, {'name': project_a.name, 'folder_id': subfolder_a.id})

        response = self.client.get('/hxt/api/projects/' + str(project_b.id))
        self.assertEqual(response.status_code, 200)
        project_b_dict = response.json()
        self.assertEqual(project_b_dict, {'name': project_b.name, 'folder_id': subfolder_b.id})

        """ Test that an unauthorized request is rejected - foreign project """

        response = self.client.get('/hxt/api/projects/' + str(foreign_project.id))
        self.assertEqual(response.status_code, 404)

        """ Test that a wrong request is rejected - not-existing project """

        response = self.client.get('/hxt/api/projects/' + str(777))
        self.assertEqual(response.status_code, 404)

    """ Test that a project is correctly created """

    def test_create_project(self):

        resp = self.client.post('/hxt/api/projects')
        self.assertEquals(resp.status_code, 401)  # unauthorized

        user = self.mock_user_session()
        foreign_user = User.objects.create(name="user", email="a@b.com")

        root_folder = RootFolder.objects.create(name="root_folder", owner=user)
        subfolder = Folder.objects.create(name="subfolder", parent_folder=root_folder)

        foreign_root_folder = RootFolder.objects.create(name="foreign_root_folder", owner=foreign_user)
        foreign_subfolder = Folder.objects.create(name="foreign_subfolder", parent_folder=foreign_root_folder)

        projs_list = list(Project.objects.all())
        self.assertTrue(len(projs_list) == 0)
        test_proj_dict = {'name': 'test_project', 'parent_folder_id': str(subfolder.id)}

        resp = self.client.post('/hxt/api/projects', json.dumps(test_proj_dict), content_type="application/json")
        self.assertEquals(resp.status_code, 201)
        projs_list = list(Project.objects.all())
        self.assertTrue(len(projs_list) == 1)

        self.assertEqual(projs_list[0].name, test_proj_dict["name"])
        folder = utils.get_folder_of_project(projs_list[0], user)
        self.assertEqual(str(folder.id), test_proj_dict["parent_folder_id"])
        # does the user have a membership in the project?
        memb = Membership.objects.filter(user=user, project=projs_list[0])
        self.assertEquals(len(memb), 1)

        """ Test that an error is returned on missing data """
        resp = self.client.post('/hxt/api/projects', json.dumps({'name': 'name', 'parent_folder_id': ''}),
                                content_type="application/json")
        self.assertEquals(resp.status_code, 400)
        self.assertEquals(resp.content.decode('utf-8'),
                          "Found empty required parameters! 'Name' or 'parent_folder_id' fields are missing")

        """ Test that an unauthorized request is rejected - foreign parent folder """

        resp2 = self.client.post('/hxt/api/projects', json.dumps({
            'name': 'name', 'parent_folder_id': str(foreign_subfolder.id)}), content_type="application/json")

        self.assertEqual(resp2.status_code, 401)
        self.assertEquals(resp2.content.decode('utf-8'),
                          "Unauthorized action! Folder " + str(foreign_subfolder.id) + " does not belong to you!")

    """ Test that a project is correctly updated """

    def test_update_project(self):

        resp = self.client.post('/hxt/api/projects')
        self.assertEquals(resp.status_code, 401)  # unauthorized

        user = self.mock_user_session()
        foreign_user = User.objects.create(name="foreign_user", email="a@a.com")

        root_folder = RootFolder.objects.create(name="root_folder", owner=user)
        subfolder = Folder.objects.create(name="subfolder", parent_folder=root_folder)
        test_project = Project.objects.create(name="test_project", created=timezone.now())
        Membership.objects.create(user=user, project=test_project)
        ProjectFolder.objects.create(project=test_project, folder=subfolder)

        foreign_project = Project.objects.create(name="foreign_project", created=timezone.now())
        Membership.objects.create(user=foreign_user, project=foreign_project)
        foreign_folder = RootFolder.objects.create(name="foreign_folder", owner=foreign_user)
        ProjectFolder.objects.create(project=foreign_project, folder=foreign_folder)

        projs_list = list(Project.objects.all())
        self.assertTrue(len(projs_list) == 2)
        proj_update = {'name': 'updated_name', 'parent_folder_id': str(root_folder.id)}
        # print("sending:" + str(proj_update))

        resp = self.client.put('/hxt/api/projects/' + str(test_project.id), json.dumps(proj_update),
                               content_type="application/json")
        print("Response:" + resp.content.decode('utf-8'))
        self.assertEquals(resp.status_code, 200)

        updated_proj = Project.objects.get(pk=test_project.id)
        self.assertEquals(proj_update['name'], updated_proj.name)

        proj_fold = utils.get_folder_of_project(updated_proj, user)
        self.assertEquals(proj_update['parent_folder_id'], str(proj_fold.id))

        """ Test that an error is returned on non-existing parent folder ID """

        proj_update = {'name': '', 'parent_folder_id': 555}
        resp = self.client.put('/hxt/api/projects/' + str(test_project.id), json.dumps(proj_update),
                               content_type="application/json")
        self.assertEquals(resp.status_code, 404)

        """ Test that an unauthorized request is rejected - foreign parent folder """

        resp2 = self.client.put('/hxt/api/projects/' + str(test_project.id), json.dumps({
            'name': '', 'parent_folder_id': str(foreign_folder.id)}), content_type="application/json")

        self.assertEqual(resp2.status_code, 401)
        self.assertEquals(resp2.content.decode('utf-8'),
                          "Unauthorized action! Folder " + str(foreign_folder.id) + " does not belong to you!")

    """ Test that a project is correctly deleted """

    def test_delete_project(self):

        resp = self.client.post('/hxt/api/projects')
        self.assertEquals(resp.status_code, 401)  # unauthorized

        user = self.mock_user_session()

        root_folder = RootFolder.objects.create(name="root_folder", owner=user)
        subfolder = Folder.objects.create(name="subfolder", parent_folder=root_folder)
        test_project = Project.objects.create(name="test_project", created=timezone.now())
        Membership.objects.create(user=user, project=test_project)
        ProjectFolder.objects.create(project=test_project, folder=subfolder)

        projs_list = list(Project.objects.all())
        self.assertTrue(len(projs_list) == 1)

        resp = self.client.delete('/hxt/api/projects/' + str(test_project.id))
        self.assertEquals(resp.status_code, 200)
        projs_list = list(Project.objects.all())
        self.assertTrue(len(projs_list) == 0)

        """ Test that an unauthorized request is rejected - cant delete a foreign project """
        foreign_project = Project.objects.create(name="foreign_project", created=timezone.now())

        resp2 = self.client.delete('/hxt/api/projects/' + str(foreign_project.id))
        self.assertEqual(resp2.status_code, 404)

    def mock_user_session(self):

        user_ext_id = 'admin'
        user = User.objects.create(name="admin", email="mail@mail.com")
        ExternalPlatform.objects.create(platform_name='atl', user_ext_id=user_ext_id, user=user)

        session = self.client.session
        session['user'] = {'userKey': user_ext_id}
        session.save()
        return user
