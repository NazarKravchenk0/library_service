from django.urls import path
from rest_framework.routers import DefaultRouter

from payments.views import PaymentViewSet, payment_cancel_view, payment_success_view


router = DefaultRouter()
router.register("", PaymentViewSet, basename="payments")

urlpatterns = router.urls + [
]

urlpatterns = [
    path("success/", payment_success_view, name="payments-success"),
    path("cancel/", payment_cancel_view, name="payments-cancel"),
] + router.urls
