from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


class UserApiTests(APITestCase):
    def test_user_registration(self):
        payload = {
            "email": "new@example.com",
            "password": "strongpass123",
            "first_name": "New",
            "last_name": "User",
        }

        response = self.client.post("/api/users/", payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(get_user_model().objects.filter(email=payload["email"]).exists())
