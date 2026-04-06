from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/users/", include("users.urls")),
    path("api/books/", include("books.urls")),
    path("api/borrowings/", include("borrowings.urls")),
    path("api/payments/", include("payments.urls")),
    path("api/users/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/users/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
