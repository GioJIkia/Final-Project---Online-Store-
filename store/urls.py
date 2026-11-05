from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views

app_name = "store"

urlpatterns = [
    path("", views.cardList, name="card-list"),
    path("register/", views.RegisterPage.as_view(), name="register"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="store:login"), name="logout"),
]


# 127.0.0.1:8000/
# 127.0.0.1:8000/register
# 127.0.0.1:8000/login
# 127.0.0.1:8000/logout
