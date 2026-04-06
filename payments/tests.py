from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment


class PaymentApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="payer@example.com",
            username="payer@example.com",
            password="payerpass123",
        )
        self.client.force_authenticate(self.user)
        book = Book.objects.create(
            title="Patterns of Enterprise Application Architecture",
            author="Martin Fowler",
            cover=Book.CoverChoices.SOFT,
            inventory=4,
            daily_fee=Decimal("4.00"),
        )
        borrowing = Borrowing.objects.create(
            book=book,
            user=self.user,
            borrow_date=timezone.localdate(),
            expected_return_date=timezone.localdate() + timezone.timedelta(days=2),
        )
        self.payment = Payment.objects.create(
            borrowing=borrowing,
            type=Payment.TypeChoices.PAYMENT,
            money_to_pay=Decimal("8.00"),
            session_id="session_test",
            session_url="https://checkout.stripe.com/pay/session_test",
        )

    def test_user_can_confirm_own_payment(self):
        response = self.client.get("/api/payments/success/?session_id=session_test")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, Payment.StatusChoices.PAID)
