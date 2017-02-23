import logging
from django.test import TestCase
from django.utils import timezone
from hetaddon.views import utils
from hetaddon.models.model import *
import json

log = logging.getLogger('django')


class RequirementViews(TestCase):

    """ Test that a requirement is correctly retrieved, given an ID """

    def test_get_requirement_by_id(self):

        resp = self.client.get('/hxt/api/requirements/' + str(1))
        self.assertEquals(resp.status_code, 401)  # unauthorized

        user = self.mock_user_session()

        test_project = Project.objects.create(name="test_project", created=timezone.now())
        Membership.objects.create(project=test_project, user=user)
        test_section = Section.objects.create(name="test_section", project=test_project)
        test_doc = Document.objects.create(name="test_doc", type="pdf", size=1353653, status="None",
                                           section=test_section, category='cal')
        test_req = Requirement.objects.create(name="test_req", project=test_project)
        test_req_value_a = RequirementValue.objects.create(value='test_req_value_a', disabled=True,
                                                           requirement=test_req, document=test_doc)
        test_req_value_b = RequirementValue.objects.create(value='test_req_value_b', disabled=True,
                                                           requirement=test_req, document=test_doc)

        # foreign data
        foreign_project = Project.objects.create(name="foreign_project", created=timezone.now())
        foreign_section = Section.objects.create(name="foreign_section", project=foreign_project)
        Document.objects.create(name="foreign_doc", type="pdf", size=1353653, status="None",
                                              section=foreign_section, category='cal')
        foreign_req = Requirement.objects.create(name="foreign_req", project=foreign_project)

        req_list = list(Requirement.objects.all())
        self.assertTrue(len(req_list) == 2)
        req_val_list = list(RequirementValue.objects.all())
        self.assertTrue(len(req_val_list) == 2)

        response = self.client.get('/hxt/api/requirements/' + str(test_req.id))
        self.assertEqual(response.status_code, 200)
        req_dict = response.json()
        self.assertEqual(req_dict,
                         {'id': test_req.id, 'name': test_req.name, 'project_id': test_project.id,
                          'values': [{'id': test_req_value_b.id, 'value': test_req_value_b.value,
                                      'disabled': test_req_value_b.disabled, 'document_id': test_req_value_b.document.id},
                                     {'id': test_req_value_a.id, 'value': test_req_value_a.value,
                                      'disabled': test_req_value_a.disabled, 'document_id': test_req_value_a.document.id}]})

        """ Test that an error is returned on unauthorized action - get foreign requirement """
        response = self.client.get('/hxt/api/requirements/' + str(foreign_req.id))
        self.assertEquals(response.status_code, 404)

        """ Test that an error is returned on requesting a non-existing requirement """
        response = self.client.get('/hxt/api/requirements/' + str(777))
        self.assertEquals(response.status_code, 404)

    """ Test that a requirement is correctly created """

    def test_create_requirement(self):

        resp = self.client.post('/hxt/api/requirements', json.dumps({}), content_type="application/json")
        self.assertEquals(resp.status_code, 401)  # unauthorized

        user = self.mock_user_session()

        test_project = Project.objects.create(name="test_project", created=timezone.now())
        Membership.objects.create(project=test_project, user=user)
        test_section = Section.objects.create(name="test_section", project=test_project)
        test_doc = Document.objects.create(name="test_doc", type="pdf", size=1353653, status="None",
                                           section=test_section, category='cal')

        foreign_project = Project.objects.create(name="foreign_project", created=timezone.now())

        req_list = list(Requirement.objects.all())
        self.assertTrue(len(req_list) == 0)

        new_req_dict = {'name': 'test_req', 'project_id': test_project.id,
                        'values': [
                            {'value': 'test_value_a', 'disabled': True, 'document_id': test_doc.id},
                            {'value': 'test_value_b', 'disabled': False, 'document_id': test_doc.id}
                        ]}

        resp = self.client.post('/hxt/api/requirements', json.dumps(new_req_dict), content_type="application/json")
        print(resp.content.decode('utf-8'))
        self.assertEquals(resp.status_code, 201)
        req_list = list(Requirement.objects.all())
        self.assertTrue(len(req_list) == 1)

        """ Test that an error is returned on wrong data """
        wrong_req = {'name': 'name', 'project_id': test_project.id}
        resp = self.client.post('/hxt/api/requirements', json.dumps(wrong_req), content_type="application/json")
        self.assertEquals(resp.status_code, 400)
        self.assertEquals(resp.content.decode('utf-8'),
                          "Missing required parameters!Expected:[name, project_id, values]")

        """ Test that an error is returned on unauthorized action - requirement with a foreign project id """
        wrong_req = {'name': 'name', 'project_id': foreign_project.id, 'values': []}
        resp = self.client.post('/hxt/api/requirements', json.dumps(wrong_req), content_type="application/json")
        self.assertEquals(resp.status_code, 404)

    """ Test that a requirement is correctly updated """

    def test_update_requirement(self):

        resp = self.client.put('/hxt/api/requirements/' + str(1), json.dumps({}), content_type="application/json")
        self.assertEquals(resp.status_code, 401)  # unauthorized

        user = self.mock_user_session()

        test_project = Project.objects.create(name="test_project", created=timezone.now())
        Membership.objects.create(project=test_project, user=user)
        test_section = Section.objects.create(name="test_section", project=test_project)
        test_doc = Document.objects.create(name="test_doc", type="pdf", size=1353653, status="None",
                                           section=test_section, category='cal')
        test_req = Requirement.objects.create(name="test_req", project=test_project)

        foreign_project = Project.objects.create(name="foreign_project", created=timezone.now())
        foreign_req = Requirement.objects.create(name="foreign_req", project=foreign_project)

        req_list = list(Requirement.objects.all())
        self.assertTrue(len(req_list) == 2)
        req_update = {'name': 'updated_name'}

        resp = self.client.put('/hxt/api/requirements/' + str(test_req.id), json.dumps(req_update),
                               content_type="application/json")
        self.assertEquals(resp.status_code, 200)
        updated_req = Requirement.objects.get(pk=test_req.id)
        self.assertEquals(updated_req.name, req_update['name'])

        """ Test that an error is returned on non-existing requirement ID """
        resp = self.client.put('/hxt/api/requirements/' + str(444), json.dumps(req_update),
                               content_type="application/json")
        self.assertEquals(resp.status_code, 404)

        """ Test that an error is returned on unauthorized request - update foreign requirement """
        resp = self.client.put('/hxt/api/requirements/' + str(foreign_req), json.dumps(req_update),
                               content_type="application/json")
        self.assertEquals(resp.status_code, 404)

    """ Test that a requirement is correctly deleted """

    def test_delete_requirement(self):

        resp = self.client.delete('/hxt/api/requirements/' + str(1))
        self.assertEquals(resp.status_code, 401)  # unauthorized

        user = self.mock_user_session()

        test_project = Project.objects.create(name="test_project", created=timezone.now())
        Membership.objects.create(project=test_project, user=user)
        test_section = Section.objects.create(name="test_section", project=test_project)
        test_doc = Document.objects.create(name="test_doc", type="pdf", size=1353653, status="None",
                                           section=test_section, category='cal')
        test_req = Requirement.objects.create(name="test_req", project=test_project)
        test_req_value_a = RequirementValue.objects.create(value='test_req_value_a', disabled=True,
                                                           requirement=test_req, document=test_doc)
        test_req_value_b = RequirementValue.objects.create(value='test_req_value_b', disabled=True,
                                                           requirement=test_req, document=test_doc)
        # foreign data
        foreign_project = Project.objects.create(name="foreign_project", created=timezone.now())
        foreign_req = Requirement.objects.create(name="foreign_req", project=foreign_project)

        req_list = list(Requirement.objects.all())
        self.assertTrue(len(req_list) == 2)
        req_val_list = list(RequirementValue.objects.all())
        self.assertTrue(len(req_val_list) == 2)

        resp = self.client.delete('/hxt/api/requirements/' + str(test_req.id))
        self.assertEquals(resp.status_code, 200)
        req_list = list(Requirement.objects.all())
        self.assertTrue(len(req_list) == 1)
        req_val_list = list(RequirementValue.objects.all())
        self.assertTrue(len(req_val_list) == 0)

        """ Test that an error is returned on unauthorized request - delete a foreign requirement """
        resp = self.client.delete('/hxt/api/requirements/' + str(foreign_req.id))
        self.assertEquals(resp.status_code, 404)

    """ Test that a all requirements of a project are correctly retrieved """

    def test_get_requirements_of_project(self):

        resp = self.client.get('/hxt/api/projects/' + str(1) + "/requirements")
        self.assertEquals(resp.status_code, 401)  # unauthorized

        user = self.mock_user_session()

        test_project_a = Project.objects.create(name="test_project_a", created=timezone.now())
        test_project_b = Project.objects.create(name="test_project_b", created=timezone.now())
        Membership.objects.create(project=test_project_a, user=user)
        Membership.objects.create(project=test_project_b, user=user)

        test_section_a = Section.objects.create(name="test_section", project=test_project_a)
        test_section_b = Section.objects.create(name="test_section", project=test_project_b)
        test_doc_a = Document.objects.create(name="test_doc_a1", type="pdf", size=111111, status="None",
                                             section=test_section_a, category='cal')
        test_req_a = Requirement.objects.create(name="test_req_a", project=test_project_a)
        test_req_val_a = RequirementValue.objects.create(value="test_req_val_a", requirement=test_req_a,
                                                         document=test_doc_a)
        test_req_b = Requirement.objects.create(name="test_req_b", project=test_project_b)
        test_req_val_b = RequirementValue.objects.create(value="test_req_val_b", requirement=test_req_b,
                                                         document=test_doc_a)
        # foreign data
        foreign_project = Project.objects.create(name="foreign_project", created=timezone.now())
        foreign_req = Requirement.objects.create(name="foreign_req", project=foreign_project)

        req_list = list(Requirement.objects.all())
        self.assertTrue(len(req_list) == 3)

        resp = self.client.get('/hxt/api/projects/' + str(test_project_a.id) + "/requirements")
        self.assertEquals(resp.status_code, 200)
        req_list = resp.json()
        self.assertEqual(req_list,
                         [{'id': test_req_a.id, 'name': test_req_a.name,
                           'values': [{'id': test_req_val_a.id, 'value': test_req_val_a.value,
                                       'disabled': test_req_val_a.disabled, 'document': test_req_val_a.document_id}]}])

        """ Test that an error is returned on non-existing project ID """
        resp = self.client.get('/hxt/api/projects/' + str(555) + "/requirements")
        self.assertEquals(resp.status_code, 404)

        """ Test that an error is returned on unauthorized request - requirement of a foreign project """
        resp = self.client.get('/hxt/api/projects/' + str(foreign_project.id) + "/requirements")
        self.assertEquals(resp.status_code, 404)

    def test_update_requirement_value(self):

        resp = self.client.put('/hxt/api/requirements/' + str(1), json.dumps({}), content_type="application/json")
        self.assertEquals(resp.status_code, 401)  # unauthorized

        user = self.mock_user_session()

        test_project = Project.objects.create(name="test_project", created=timezone.now())
        Membership.objects.create(project=test_project, user=user)
        test_section = Section.objects.create(name="test_section", project=test_project)
        test_doc = Document.objects.create(name="test_doc", type="pdf", size=1353653, status="None",
                                           section=test_section, category='cal')
        test_req = Requirement.objects.create(name="test_req", project=test_project)
        test_req_value_a = RequirementValue.objects.create(value='test_req_value_a', disabled=True,
                                                           requirement=test_req, document=test_doc)
        test_req_value_b = RequirementValue.objects.create(value='test_req_value_b', disabled=True,
                                                           requirement=test_req, document=test_doc)
        # foreign data
        foreign_project = Project.objects.create(name="foreign_project", created=timezone.now())
        foreign_req = Requirement.objects.create(name="foreign_req", project=foreign_project)

        req_val_list = list(RequirementValue.objects.all())
        self.assertTrue(len(req_val_list) == 2)
        req_update = {'value': 'updated_value'}

        resp = self.client.put('/hxt/api/values/' + str(test_req_value_a.id), json.dumps(req_update), content_type="application/json")

        self.assertEquals(resp.status_code, 200)
        updated_req_val = RequirementValue.objects.get(pk=test_req_value_a.id)
        self.assertEquals(req_update['value'], updated_req_val.value)

        """ Test that an error is returned on non-existing requirement ID """

        resp = self.client.put('/hxt/api/requirements/' + str(444), json.dumps(req_update),
                               content_type="application/json")
        self.assertEquals(resp.status_code, 404)

    def mock_user_session(self):
        user_ext_id = 'admin'
        user = User.objects.create(name="admin", email="mail@mail.com")
        ExternalPlatform.objects.create(platform_name='atl', user_ext_id=user_ext_id, user=user)

        session = self.client.session
        session['user'] = {'userKey': user_ext_id}
        session.save()
        return user
