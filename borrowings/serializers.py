from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from books.models import Book
from books.serializers import BookSerializer
from borrowings.models import Borrowing
from notifications.tasks import notify_new_borrowing_task
from payments.models import Payment
from payments.serializers import PaymentSerializer
from payments.services import create_payment_session


class BorrowingListSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "payments",
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "book", "borrow_date", "expected_return_date")

    def validate_book(self, value: Book):
        if value.inventory < 1:
            raise serializers.ValidationError("This book is out of stock.")
        return value

    def validate(self, attrs):
        borrow_date = attrs.get("borrow_date", timezone.localdate())
        expected_return_date = attrs["expected_return_date"]
        if expected_return_date < borrow_date:
            raise serializers.ValidationError(
                {"expected_return_date": "Expected return date cannot be earlier than borrow date."}
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        book = validated_data["book"]
        book.inventory -= 1
        book.save(update_fields=["inventory"])

        borrowing = Borrowing.objects.create(
            user=self.context["request"].user,
            **validated_data,
        )
        create_payment_session(borrowing, request=self.context.get("request"))
        notify_new_borrowing_task.delay(borrowing.id)
        return borrowing


class BorrowingDetailSerializer(BorrowingListSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)

    class Meta(BorrowingListSerializer.Meta):
        fields = BorrowingListSerializer.Meta.fields + ("user_id",)


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "actual_return_date")
        read_only_fields = ("id",)

    def validate_actual_return_date(self, value):
        borrowing = self.instance
        if borrowing.actual_return_date:
            raise serializers.ValidationError("This borrowing has already been returned.")
        if value < borrowing.borrow_date:
            raise serializers.ValidationError("Actual return date cannot be earlier than borrow date.")
        return value

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.actual_return_date = validated_data["actual_return_date"]
        instance.full_clean()
        instance.save(update_fields=["actual_return_date"])

        book = instance.book
        book.inventory += 1
        book.save(update_fields=["inventory"])

        overdue_days = (instance.actual_return_date - instance.expected_return_date).days
        if overdue_days > 0:
            fine_amount = (
                Decimal(overdue_days)
                * instance.book.daily_fee
                * Decimal(settings.FINE_MULTIPLIER)
            )
            create_payment_session(
                instance,
                payment_type=Payment.TypeChoices.FINE,
                amount=fine_amount,
                request=self.context.get("request"),
            )

        return instance
