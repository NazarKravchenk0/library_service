from django.db import models


class Notification(models.Model):
    class TypeChoices(models.TextChoices):
        NEW_BORROWING = "NEW_BORROWING", "New borrowing"
        OVERDUE = "OVERDUE", "Overdue"
        PAYMENT_SUCCESS = "PAYMENT_SUCCESS", "Payment success"

    class StatusChoices(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SENT = "SENT", "Sent"
        FAILED = "FAILED", "Failed"

    type = models.CharField(max_length=20, choices=TypeChoices.choices)
    message = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )
    borrowing = models.ForeignKey(
        "borrowings.Borrowing",
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )
    payment = models.ForeignKey(
        "payments.Payment",
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        return f"Notification #{self.pk} ({self.type})"
