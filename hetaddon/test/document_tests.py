import base64
import logging
from django.test import TestCase
from django.utils import timezone

from hetaddon.models.model import *
import json

log = logging.getLogger('django')


class DocumentViews(TestCase):

    """ Test that a document is correctly retrieved, given an ID """

    def test_get_document_by_id(self):

        resp = self.client.get('/hxt/api/documents/' + str(1))
        self.assertEquals(resp.status_code, 401)  # unauthorized

        user = self.mock_user_session()

        root_folder = RootFolder.objects.create(name="root_folder", owner=user)
        subfolder = Folder.objects.create(name="subfolder", parent_folder=root_folder)
        test_project = Project.objects.create(name="test_project", created=timezone.now())
        Membership.objects.create(project=test_project, user=user)
        ProjectFolder.objects.create(project=test_project, folder=subfolder)
        test_section = Section.objects.create(name="test_section", project=test_project)
        test_doc = Document.objects.create(name="test_doc", type="pdf", size=1353653, status="None",
                                           section=test_section, category='cal')

        foreign_project = Project.objects.create(name="foreign_project", created=timezone.now())
        foreign_section = Section.objects.create(name="foreign_section", project=foreign_project)
        foreign_doc = Document.objects.create(name="foreign_doc", type="pdf", size=1353653, status="None",
                                           section=foreign_section, category='cal')

        response = self.client.get('/hxt/api/documents/' + str(test_doc.id))
        # print("response:" + response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        doc_dict = response.json()
        self.assertEqual(doc_dict,
                         {'id': test_doc.id, 'category': test_doc.category, 'name': test_doc.name,
                          'section_id': test_doc.section_id, 'size': test_doc.size, 'type': test_doc.type})

        response = self.client.get('/hxt/api/documents/' + str(test_doc.id))
        # print("response:" + response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 200)

        """ Test that an error is returned on unauthorized request - document not belonging to user """

        resp = self.client.get('/hxt/api/documents/' + str(foreign_doc.id))
        self.assertEquals(resp.status_code, 401)
        self.assertEquals(resp.content.decode('utf-8'), "Document " + str(foreign_doc.id) + " is not yours!")

    """ Test that a document is correctly created for a given user """

    def test_create_document(self):

        resp = self.client.post('/hxt/api/documents', json.dumps({}), content_type="application/json")
        self.assertEquals(resp.status_code, 401)  # unauthorized

        user = self.mock_user_session()

        root_folder = RootFolder.objects.create(name="root_folder", owner=user)
        subfolder = Folder.objects.create(name="subfolder", parent_folder=root_folder)
        test_project = Project.objects.create(name="test_project", created=timezone.now())
        Membership.objects.create(project=test_project, user=user)
        ProjectFolder.objects.create(project=test_project, folder=subfolder)
        test_section = Section.objects.create(name="test_section", project=test_project)

        foreign_project = Project.objects.create(name="foreign_project", created=timezone.now())
        foreign_section = Section.objects.create(name="foreign_section", project=foreign_project)

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
        # print("response:" + resp.content.decode('utf-8'))

        # TODO: test that the binary content is being correctly stored (i was unable to retrieve it back)

        """ Test that an error is returned on missing data """
        resp = self.client.post('/hxt/api/documents', json.dumps({'name': 'name', 'section_id': ''}),
                                content_type="application/json")
        self.assertEquals(resp.status_code, 400)
        self.assertEquals(resp.content.decode('utf-8'),
                          "Unexpected structure! Missing required parameters")

        """ Test that an error is returned on unauthorized action - document with foreign section """
        resp = self.client.post('/hxt/api/documents', json.dumps({
            'name': 'name', 'type': 'pdf', 'size': 11111, 'section_id': str(foreign_section.id), 'category': 'cal',
            'content': bin_doc_content.decode('utf-8')}),
                                content_type="application/json")

        # print("last response:" + resp.content.decode('utf-8'))
        self.assertEquals(resp.status_code, 401)
        self.assertEquals(resp.content.decode('utf-8'), "Section 2 is not yours!")

    """ Test that a document is correctly updated """

    def test_update_document(self):

        resp = self.client.put('/hxt/api/documents/' + str(1), json.dumps({}), content_type="application/json")
        self.assertEquals(resp.status_code, 401)  # unauthorized

        user = self.mock_user_session()

        root_folder = RootFolder.objects.create(name="root_folder", owner=user)
        subfolder = Folder.objects.create(name="subfolder", parent_folder=root_folder)
        test_project = Project.objects.create(name="test_project", created=timezone.now())
        Membership.objects.create(project=test_project, user=user)
        ProjectFolder.objects.create(project=test_project, folder=subfolder)
        test_section = Section.objects.create(name="test_section", project=test_project)
        test_doc = Document.objects.create(name="test_doc", type="pdf", size=1353653, status="None",
                                           section=test_section, category='cal')

        foreign_project = Project.objects.create(name="foreign_project", created=timezone.now())
        foreign_section = Section.objects.create(name="foreign_section", project=foreign_project)

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

        """ Test that an error is returned on foreign section ID """

        doc_update = {'name': 'updated_name', 'type': '', 'size': '', 'category': '', 'section_id': str(foreign_section.id)}
        resp = self.client.put('/hxt/api/documents/' + str(test_doc.id), json.dumps(doc_update),
                               content_type="application/json")
        self.assertEquals(resp.status_code, 401)
        self.assertEquals(resp.content.decode('utf-8'), "Section " + str(foreign_section.id) + " is not yours!")

    """ Test that a document is correctly deleted """

    def test_delete_document(self):

        resp = self.client.delete('/hxt/api/documents/' + str(1))
        self.assertEquals(resp.status_code, 401)  # unauthorized

        user = self.mock_user_session()

        root_folder = RootFolder.objects.create(name="root_folder", owner=user)
        subfolder = Folder.objects.create(name="subfolder", parent_folder=root_folder)
        test_project = Project.objects.create(name="test_project", created=timezone.now())
        Membership.objects.create(project=test_project, user=user)
        ProjectFolder.objects.create(project=test_project, folder=subfolder)
        test_section = Section.objects.create(name="test_section", project=test_project)
        test_doc = Document.objects.create(name="test_doc", type="pdf", size=1353653, status="None",
                                           section=test_section, category='cal')

        foreign_project = Project.objects.create(name="foreign_project", created=timezone.now())
        foreign_section = Section.objects.create(name="foreign_section", project=foreign_project)
        foreign_doc = Document.objects.create(name="foreign_doc", type="pdf", size=1353653, status="None",
                                              section=foreign_section, category='cal')

        docs_list = list(Document.objects.all())
        self.assertTrue(len(docs_list) == 2)

        resp = self.client.delete('/hxt/api/documents/' + str(test_doc.id))
        # print("del response:" + resp.content.decode('utf-8'))
        self.assertEquals(resp.status_code, 200)
        docs_list = list(Document.objects.all())
        self.assertTrue(len(docs_list) == 1)

        """ Test that an error is returned when attempting to delete a foreign doc """
        resp = self.client.delete('/hxt/api/documents/' + str(foreign_doc.id))
        docs_list = list(Document.objects.all())
        self.assertTrue(len(docs_list) == 1)
        self.assertEquals(resp.status_code, 401)
        self.assertEquals(resp.content.decode('utf-8'), "Document " + str(foreign_doc.id) + " is not yours!")

        """ Test that an error is returned when attempting to delete a non-existing doc """
        resp = self.client.delete('/hxt/api/documents/' + str(777))
        docs_list = list(Document.objects.all())
        self.assertTrue(len(docs_list) == 1)
        self.assertEquals(resp.status_code, 404)

    """ Test that a all documents of a project are correctly retrieved """

    def test_get_documents_of_project(self):

        resp = self.client.get('/hxt/api/projects/' + str(1) + "/documents")
        self.assertEquals(resp.status_code, 401)  # unauthorized

        user = self.mock_user_session()

        root_folder = RootFolder.objects.create(name="root_folder", owner=user)
        subfolder = Folder.objects.create(name="subfolder", parent_folder=root_folder)
        test_project = Project.objects.create(name="test_project", created=timezone.now())
        Membership.objects.create(project=test_project, user=user)
        ProjectFolder.objects.create(project=test_project, folder=subfolder)
        test_section = Section.objects.create(name="test_section", project=test_project)
        test_section_b = Section.objects.create(name="test_section_b", project=test_project)
        test_doc_a = Document.objects.create(name="test_doca", type="pdf", size=1353653, status="None",
                                           section=test_section, category='cal')
        test_doc_b = Document.objects.create(name="test_docb", type="pdf", size=1353653, status="None",
                                           section=test_section_b, category='cal')

        foreign_project = Project.objects.create(name="foreign_project", created=timezone.now())
        foreign_section = Section.objects.create(name="foreign_section", project=foreign_project)
        foreign_doc = Document.objects.create(name="foreign_doc", type="pdf", size=1353653, status="None",
                                              section=foreign_section, category='cal')

        doc_list = list(Document.objects.all())
        self.assertTrue(len(doc_list) == 3)

        resp = self.client.get('/hxt/api/projects/' + str(test_project.id) + "/documents")
        self.assertEquals(resp.status_code, 200)
        doc_list = resp.json()
        self.assertEqual(doc_list,
                         [{'id': test_doc_a.id, 'name': test_doc_a.name, 'type': test_doc_a.type,
                           'size': test_doc_a.size, 'status': 'None', 'category': test_doc_a.category,
                           'section_id': test_doc_a.section_id},
                          {'id': test_doc_b.id, 'name': test_doc_b.name, 'type': test_doc_b.type,
                           'size': test_doc_b.size, 'status': 'None', 'category': test_doc_b.category,
                           'section_id': test_doc_b.section_id},
                          ])

        """ Test that an error is returned on non-existing project ID """
        resp = self.client.get('/hxt/api/projects/' + str(555) + "/documents")
        self.assertEquals(resp.status_code, 404)

        """ Test that an error is returned on request containing a foreign project ID """
        resp = self.client.get('/hxt/api/projects/' + str(foreign_project.id) + "/documents")
        self.assertEquals(resp.status_code, 404)

    def mock_user_session(self):

        user_ext_id = 'admin'
        user = User.objects.create(name="admin", email="mail@mail.com")
        ExternalPlatform.objects.create(platform_name='atl', user_ext_id=user_ext_id, user=user)

        session = self.client.session
        session['user'] = {'userKey': user_ext_id}
        session.save()
        return user
