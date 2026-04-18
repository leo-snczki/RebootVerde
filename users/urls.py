from django.urls import path, include
from . import views  

urlpatterns = [
    path("accounts/register/", views.register_user, name="register"),
    path("accounts/verify/", views.verify_code, name="verify_code"),
    path("", views.index, name="index"),
    path("shop/", views.shop, name="shop"),
    path("accounts/", include("django.contrib.auth.urls")),
]