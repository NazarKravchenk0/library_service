from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment


class BorrowingApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="reader@example.com",
            username="reader@example.com",
            password="readerpass123",
        )
        self.book = Book.objects.create(
            title="Refactoring",
            author="Martin Fowler",
            cover=Book.CoverChoices.HARD,
            inventory=2,
            daily_fee=Decimal("3.00"),
        )
        self.client.force_authenticate(self.user)

    def test_create_borrowing_decreases_inventory_and_creates_payment(self):
        payload = {
            "book": self.book.id,
            "borrow_date": str(timezone.localdate()),
            "expected_return_date": str(timezone.localdate() + timezone.timedelta(days=3)),
        }

        response = self.client.post("/api/borrowings/", payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 1)
        borrowing = Borrowing.objects.get()
        self.assertEqual(borrowing.user, self.user)
        self.assertEqual(Payment.objects.filter(borrowing=borrowing).count(), 1)

    def test_return_borrowing_restores_inventory_and_creates_fine(self):
        borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            borrow_date=timezone.localdate(),
            expected_return_date=timezone.localdate(),
        )

        response = self.client.post(
            f"/api/borrowings/{borrowing.id}/return/",
            {"actual_return_date": str(timezone.localdate() + timezone.timedelta(days=2))},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 3)
        self.assertTrue(
            Payment.objects.filter(borrowing=borrowing, type=Payment.TypeChoices.FINE).exists()
        )
