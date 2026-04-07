from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from books.models import Book


class BookApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            username="user@example.com",
            password="testpass123",
        )
        self.admin = get_user_model().objects.create_superuser(
            email="admin@example.com",
            username="admin@example.com",
            password="adminpass123",
        )

    def test_books_list_is_public(self):
        Book.objects.create(
            title="Clean Code",
            author="Robert Martin",
            cover=Book.CoverChoices.HARD,
            inventory=3,
            daily_fee=Decimal("1.50"),
        )

        response = self.client.get("/api/books/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_only_admin_can_create_book(self):
        payload = {
            "title": "Domain-Driven Design",
            "author": "Eric Evans",
            "cover": Book.CoverChoices.SOFT,
            "inventory": 5,
            "daily_fee": "2.00",
        }

        self.client.force_authenticate(self.user)
        response = self.client.post("/api/books/", payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.admin)
        response = self.client.post("/api/books/", payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
