from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from django.conf import settings
import stripe

from payments.models import Payment
from payments.serializers import PaymentSerializer
from notifications.tasks import notify_payment_success_task


stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Payment.objects.select_related("borrowing", "borrowing__user")
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(borrowing__user=self.request.user)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def payment_success_view(request):
    session_id = request.query_params.get("session_id")
    if not session_id:
        return Response({"detail": "session_id query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

    payment = Payment.objects.filter(session_id=session_id).first()
    if not payment:
        return Response({"detail": "Payment not found."}, status=status.HTTP_404_NOT_FOUND)

    if not request.user.is_staff and payment.borrowing.user != request.user:
        return Response({"detail": "You do not have permission to access this payment."}, status=status.HTTP_403_FORBIDDEN)

    if settings.STRIPE_SECRET_KEY:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status != "paid":
            return Response({"detail": "Stripe session is not paid yet."}, status=status.HTTP_400_BAD_REQUEST)

    payment.status = Payment.StatusChoices.PAID
    payment.save(update_fields=["status"])
    notify_payment_success_task.delay(payment.id)
    return Response({"detail": "Payment successfully confirmed."})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def payment_cancel_view(request):
    return Response({"detail": "Payment was cancelled. You can complete it later within 24 hours."})
