from celery import shared_task
from django.utils import timezone

from borrowings.models import Borrowing
from notifications.models import Notification
from notifications.services import send_telegram_message


def _create_notification(
    *,
    notification_type: str,
    message: str,
    borrowing=None,
    payment=None,
) -> Notification:
    is_sent = send_telegram_message(message)
    return Notification.objects.create(
        type=notification_type,
        message=message,
        status=Notification.StatusChoices.SENT
        if is_sent
        else Notification.StatusChoices.FAILED,
        borrowing=borrowing,
        payment=payment,
        sent_at=timezone.now() if is_sent else None,
    )


@shared_task
def notify_new_borrowing_task(borrowing_id: int) -> None:
    borrowing = Borrowing.objects.select_related("book", "user").get(id=borrowing_id)
    message = (
        (
            "New borrowing created\n"
            f"Borrowing ID: {borrowing.id}\n"
            f"Book: {borrowing.book.title}\n"
            f"User: {borrowing.user.email}\n"
            f"Borrow date: {borrowing.borrow_date}\n"
            f"Expected return: {borrowing.expected_return_date}"
        )
    )
    _create_notification(
        notification_type=Notification.TypeChoices.NEW_BORROWING,
        message=message,
        borrowing=borrowing,
    )


@shared_task
def notify_overdue_borrowings() -> None:
    today = timezone.localdate()
    overdue_borrowings = Borrowing.objects.filter(
        actual_return_date__isnull=True,
        expected_return_date__lte=today,
    ).select_related("book", "user")

    if not overdue_borrowings.exists():
        _create_notification(
            notification_type=Notification.TypeChoices.OVERDUE,
            message="No borrowings overdue today!",
        )
        return

    for borrowing in overdue_borrowings:
        message = (
            (
                "Overdue borrowing detected\n"
                f"Borrowing ID: {borrowing.id}\n"
                f"Book: {borrowing.book.title}\n"
                f"User: {borrowing.user.email}\n"
                f"Expected return: {borrowing.expected_return_date}"
            )
        )
        _create_notification(
            notification_type=Notification.TypeChoices.OVERDUE,
            message=message,
            borrowing=borrowing,
        )


@shared_task
def notify_payment_success_task(payment_id: int) -> None:
    from payments.models import Payment

    payment = Payment.objects.select_related("borrowing", "borrowing__book", "borrowing__user").get(id=payment_id)
    message = (
        (
            "Payment completed\n"
            f"Payment ID: {payment.id}\n"
            f"Type: {payment.type}\n"
            f"User: {payment.borrowing.user.email}\n"
            f"Book: {payment.borrowing.book.title}\n"
            f"Amount: ${payment.money_to_pay}"
        )
    )
    _create_notification(
        notification_type=Notification.TypeChoices.PAYMENT_SUCCESS,
        message=message,
        borrowing=payment.borrowing,
        payment=payment,
    )
