
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

import base64

from hetaddon.models.model import *
import json


class IndexView(TestCase):

    """ Test the index view page rendering """

    """ Test that the index view is available on equivalent URLs """

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/hxt/')
        self.assertEqual(response.status_code, 200)


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
        doc_update = {'name': 'updated_name'}

        resp = self.client.put('/hxt/api/documents/' + str(test_doc.id), json.dumps(doc_update),
                               content_type="application/json")
        self.assertEquals(resp.status_code, 200)
        updated_doc = Document.objects.get(pk=test_doc.id)
        self.assertEquals(updated_doc.name, doc_update['name'])

        """ Test that an error is returned on non-existing section ID """

        doc_update = {'name': 'updated_name', 'type': '', 'size': '', 'category': '', 'section_id': 555}
        resp = self.client.put('/hxt/api/documents/' + str(test_doc.id), json.dumps(doc_update),
                               content_type="application/json")
        self.assertEquals(resp.status_code, 404)

    """ Test that a document is correctly deleted """

    def test_delete_document(self):

        test_folder = Folder.objects.create(name="test_folder", parent_folder=None)
        test_project = Project.objects.create(name="test_project", created=timezone.now(), folder=test_folder)
        test_section = Section.objects.create(name="test_section", project=test_project)
        test_doc = Document.objects.create(name="test_doc", type="pdf", size=111111, status="None",
                                           section=test_section, category='cal')

        docs_list = list(Document.objects.all())
        self.assertTrue(len(docs_list) == 1)

        resp = self.client.delete('/hxt/api/documents/' + str(test_doc.id))
        self.assertEquals(resp.status_code, 200)
        docs_list = list(Document.objects.all())
        self.assertTrue(len(docs_list) == 0)

    """ Test that a all documents of a project are correctly retrieved """

    def test_get_documents_of_project(self):

        test_folder = Folder.objects.create(name="test_folder", parent_folder=None)
        test_project_a = Project.objects.create(name="test_project_a", created=timezone.now(), folder=test_folder)
        test_project_b = Project.objects.create(name="test_project_b", created=timezone.now(), folder=test_folder)
        test_section_a = Section.objects.create(name="test_section", project=test_project_a)
        test_section_b = Section.objects.create(name="test_section", project=test_project_b)
        test_doc_a1 = Document.objects.create(name="test_doc_a1", type="pdf", size=111111, status="None",
                                             section=test_section_a, category='cal')
        test_doc_a2 = Document.objects.create(name="test_doc_a2", type="pdf", size=111111, status="None",
                                             section=test_section_a, category='cal')
        test_doc_b = Document.objects.create(name="test_doc_b", type="pdf", size=111111, status="None",
                                             section=test_section_b, category='cal')

        doc_list = list(Document.objects.all())
        self.assertTrue(len(doc_list) == 3)

        resp = self.client.post('/hxt/api/projects/' + str(test_project_a.id) + "/documents")
        self.assertEquals(resp.status_code, 200)
        doc_list = resp.json()
        self.assertTrue(type(doc_list) is list)
        self.assertEqual(doc_list,
                         [{'id': test_doc_a1.id, 'name': test_doc_a1.name, 'type': test_doc_a1.type,
                           'size': test_doc_a1.size, 'status': 'None', 'category': test_doc_a1.category,
                           'section_id': test_doc_a1.section_id},
                          {'id': test_doc_a2.id, 'name': test_doc_a2.name, 'type': test_doc_a2.type,
                           'size': test_doc_a2.size, 'status': 'None', 'category': test_doc_a2.category,
                           'section_id': test_doc_a2.section_id},
                          ])

        """ Test that an error is returned on non-existing project ID """

        resp = self.client.get('/hxt/api/projects/' + str(555) + "/documents")
        self.assertEquals(resp.status_code, 404)


class RequirementViews(TestCase):

    """ Test that a requirement is correctly retrieved, given an ID """

    def test_get_requirement_by_id(self):

        test_folder = Folder.objects.create(name="test_folder", parent_folder=None)
        test_project = Project.objects.create(name="test_project", created=timezone.now(), folder=test_folder)
        test_section = Section.objects.create(name="test_section", project=test_project)
        test_doc = Document.objects.create(name="test_doc", type="pdf", size=1353653, status="None",
                                           section=test_section, category='cal')
        test_req = Requirement.objects.create(name="test_req", project=test_project)
        test_req_value_a = RequirementValue.objects.create(value='test_req_value_a', disabled=True,
                                                           requirement=test_req, document=test_doc)
        test_req_value_b = RequirementValue.objects.create(value='test_req_value_b', disabled=True,
                                                           requirement=test_req, document=test_doc)

        req_list = list(Requirement.objects.all())
        self.assertTrue(len(req_list) == 1)
        req_val_list = list(RequirementValue.objects.all())
        self.assertTrue(len(req_val_list) == 2)

        response = self.client.get('/hxt/api/requirements/' + str(test_req.id))
        self.assertEqual(response.status_code, 200)
        req_dict = response.json()
        self.assertTrue(type(req_dict) is dict)
        self.assertEqual(req_dict,
                         {'id': test_req.id, 'name': test_req.name, 'project_id': test_project.id,
                          'values': [{'id': test_req_value_b.id, 'value': test_req_value_b.value,
                                      'disabled': test_req_value_b.disabled, 'document_id': test_req_value_b.document.id},
                                     {'id': test_req_value_a.id, 'value': test_req_value_a.value,
                                      'disabled': test_req_value_a.disabled, 'document_id': test_req_value_a.document.id}]})

    """ Test that a requirement is correctly created """

    def test_create_requirement(self):

        test_folder = Folder.objects.create(name="test_folder", parent_folder=None)
        test_project = Project.objects.create(name="test_project", created=timezone.now(), folder=test_folder)
        test_section = Section.objects.create(name="test_section", project=test_project)
        test_doc = Document.objects.create(name="test_doc", type="pdf", size=1353653, status="None",
                                           section=test_section, category='cal')

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

    """ Test that a requirement is correctly updated """

    def test_update_requirement(self):

        test_folder = Folder.objects.create(name="test_folder", parent_folder=None)
        test_project = Project.objects.create(name="test_project", created=timezone.now(), folder=test_folder)
        test_section = Section.objects.create(name="test_section", project=test_project)
        test_doc = Document.objects.create(name="test_doc", type="pdf", size=1353653, status="None",
                                           section=test_section, category='cal')
        test_req = Requirement.objects.create(name="test_req", project=test_project)

        req_list = list(Requirement.objects.all())
        self.assertTrue(len(req_list) == 1)
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

    """ Test that a requirement is correctly deleted """

    def test_delete_requirement(self):

        test_folder = Folder.objects.create(name="test_folder", parent_folder=None)
        test_project = Project.objects.create(name="test_project", created=timezone.now(), folder=test_folder)
        test_section = Section.objects.create(name="test_section", project=test_project)
        test_doc = Document.objects.create(name="test_doc", type="pdf", size=1353653, status="None",
                                           section=test_section, category='cal')
        test_req = Requirement.objects.create(name="test_req", project=test_project)
        RequirementValue.objects.create(value='test_req_value_a', disabled=True,
                                        requirement=test_req, document=test_doc)
        RequirementValue.objects.create(value='test_req_value_b', disabled=True,
                                        requirement=test_req, document=test_doc)

        req_list = list(Requirement.objects.all())
        self.assertTrue(len(req_list) == 1)
        req_val_list = list(RequirementValue.objects.all())
        self.assertTrue(len(req_val_list) == 2)
        resp = self.client.delete('/hxt/api/requirements/' + str(test_req.id))
        self.assertEquals(resp.status_code, 200)
        req_list = list(Requirement.objects.all())
        self.assertTrue(len(req_list) == 0)
        req_val_list = list(RequirementValue.objects.all())
        self.assertTrue(len(req_val_list) == 0)

    """ Test that a all requirements of a project are correctly retrieved """

    def test_get_requirements_of_project(self):

        test_folder = Folder.objects.create(name="test_folder", parent_folder=None)
        test_project_a = Project.objects.create(name="test_project_a", created=timezone.now(), folder=test_folder)
        test_project_b = Project.objects.create(name="test_project_b", created=timezone.now(), folder=test_folder)
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

        req_list = list(Requirement.objects.all())
        self.assertTrue(len(req_list) == 2)

        resp = self.client.get('/hxt/api/projects/' + str(test_project_a.id) + "/requirements")
        self.assertEquals(resp.status_code, 200)
        req_list = resp.json()
        self.assertTrue(type(req_list) is list)
        # print(req_list)
        self.assertEqual(req_list,
                         [{'id': test_req_a.id, 'name': test_req_a.name,
                           'values': [{'id': test_req_val_a.id, 'value': test_req_val_a.value,
                                       'disabled': test_req_val_a.disabled, 'document': test_req_val_a.document_id}]}])

        """ Test that an error is returned on non-existing project ID """

        resp = self.client.get('/hxt/api/projects/' + str(555) + "/requirements")
        self.assertEquals(resp.status_code, 404)

    def test_update_requirement_value(self):

        test_folder = Folder.objects.create(name="test_folder", parent_folder=None)
        test_project = Project.objects.create(name="test_project", created=timezone.now(), folder=test_folder)
        test_section = Section.objects.create(name="test_section", project=test_project)
        test_doc = Document.objects.create(name="test_doc", type="pdf", size=1353653, status="None",
                                           section=test_section, category='cal')
        test_req = Requirement.objects.create(name="test_req", project=test_project)
        test_req_value = RequirementValue.objects.create(value="Innovating SMEs", requirement=test_req,
                                                         document=test_doc)

        req_val_list = list(RequirementValue.objects.all())
        self.assertTrue(len(req_val_list) == 1)
        req_update = {'value': 'updated_value'}

        resp = self.client.put('/hxt/api/values/' + str(test_req_value.id),
                               json.dumps(req_update), content_type="application/json")

        self.assertEquals(resp.status_code, 200)
        updated_req_val = RequirementValue.objects.get(pk=test_req_value.id)
        self.assertEquals(updated_req_val.value, req_update['value'])

        """ Test that an error is returned on non-existing requirement ID """

        resp = self.client.put('/hxt/api/requirements/' + str(444), json.dumps(req_update),
                               content_type="application/json")
        self.assertEquals(resp.status_code, 404)
