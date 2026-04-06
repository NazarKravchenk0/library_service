from django.urls import path

from users.views import ManageUserView, UserCreateView


urlpatterns = [
    path("", UserCreateView.as_view(), name="create-user"),
    path("me/", ManageUserView.as_view(), name="manage-user"),
]
