from celery import shared_task
from django.utils import timezone

from borrowings.models import Borrowing
from notifications.services import send_telegram_message


@shared_task
def notify_new_borrowing_task(borrowing_id: int) -> None:
    borrowing = Borrowing.objects.select_related("book", "user").get(id=borrowing_id)
    send_telegram_message(
        (
            "New borrowing created\n"
            f"Borrowing ID: {borrowing.id}\n"
            f"Book: {borrowing.book.title}\n"
            f"User: {borrowing.user.email}\n"
            f"Borrow date: {borrowing.borrow_date}\n"
            f"Expected return: {borrowing.expected_return_date}"
        )
    )


@shared_task
def notify_overdue_borrowings() -> None:
    today = timezone.localdate()
    overdue_borrowings = Borrowing.objects.filter(
        actual_return_date__isnull=True,
        expected_return_date__lte=today,
    ).select_related("book", "user")

    if not overdue_borrowings.exists():
        send_telegram_message("No borrowings overdue today!")
        return

    for borrowing in overdue_borrowings:
        send_telegram_message(
            (
                "Overdue borrowing detected\n"
                f"Borrowing ID: {borrowing.id}\n"
                f"Book: {borrowing.book.title}\n"
                f"User: {borrowing.user.email}\n"
                f"Expected return: {borrowing.expected_return_date}"
            )
        )


@shared_task
def notify_payment_success_task(payment_id: int) -> None:
    from payments.models import Payment

    payment = Payment.objects.select_related("borrowing", "borrowing__book", "borrowing__user").get(id=payment_id)
    send_telegram_message(
        (
            "Payment completed\n"
            f"Payment ID: {payment.id}\n"
            f"Type: {payment.type}\n"
            f"User: {payment.borrowing.user.email}\n"
            f"Book: {payment.borrowing.book.title}\n"
            f"Amount: ${payment.money_to_pay}"
        )
    )
