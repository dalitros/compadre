from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

class IndexViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_index_get(self):
        url = reverse('index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)