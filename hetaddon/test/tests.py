from django.test import TestCase
from django.urls import reverse


class IndexView(TestCase):

    """ Test the index view page rendering """

    """ Test that the index view is available on equivalent URLs """

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/hxt/')
        self.assertEqual(response.status_code, 200)

