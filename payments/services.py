from decimal import Decimal
from uuid import uuid4

from django.urls import reverse
import stripe

from django.conf import settings
from payments.models import Payment


stripe.api_key = settings.STRIPE_SECRET_KEY


def calculate_borrowing_payment(borrowing) -> Decimal:
    days = (borrowing.expected_return_date - borrowing.borrow_date).days
    return Decimal(max(days, 1)) * borrowing.book.daily_fee


def _build_absolute_url(request, route_name: str) -> str:
    relative_url = reverse(route_name)
    if request:
        return request.build_absolute_uri(relative_url)
    return f"http://localhost:8000{relative_url}"


def _create_stripe_checkout_session(amount: Decimal, borrowing, request):
    success_url = f"{_build_absolute_url(request, 'payments-success')}?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = _build_absolute_url(request, "payments-cancel")
    session = stripe.checkout.Session.create(
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": int(amount * 100),
                    "product_data": {
                        "name": borrowing.book.title,
                        "description": f"{borrowing.book.author} | borrowing #{borrowing.id}",
                    },
                },
                "quantity": 1,
            }
        ],
    )
    return session.url, session.id


def create_payment_session(borrowing, payment_type=Payment.TypeChoices.PAYMENT, amount=None, request=None):
    amount = amount if amount is not None else calculate_borrowing_payment(borrowing)
    if settings.STRIPE_SECRET_KEY:
        session_url, session_id = _create_stripe_checkout_session(amount, borrowing, request)
    else:
        session_id = f"session_{uuid4().hex}"
        success_url = f"{_build_absolute_url(request, 'payments-success')}?session_id={session_id}"
        cancel_url = _build_absolute_url(request, "payments-cancel")
        session_url = (
            f"https://checkout.stripe.com/pay/{session_id}"
            f"?success_url={success_url}&cancel_url={cancel_url}"
        )

    return Payment.objects.create(
        borrowing=borrowing,
        type=payment_type,
        money_to_pay=amount,
        session_url=session_url,
        session_id=session_id,
        status=Payment.StatusChoices.PENDING,
    )
