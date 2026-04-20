from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("accounts/register/", views.register_user, name="register"),
    path("accounts/verify/", views.verify_code, name="verify_code"),
    path("accounts/password_reset/", auth_views.PasswordResetView.as_view(
        template_name="users/password_reset_form.html",
        email_template_name="users/password_reset_email.html"
    ), name="password_reset"),

    path("accounts/password_reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name="users/password_reset_done.html"
    ), name="password_reset_done"),

    path("accounts/reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="users/password_reset_confirm.html"
    ), name="password_reset_confirm"),

    path("accounts/reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name="users/password_reset_complete.html"
    ), name="password_reset_complete"),
    path("accounts/logout/", auth_views.LogoutView.as_view(template_name="users/logout.html"), name="logout"),
    path("accounts/profile/", views.profile, name="profile"),
    
    path("accounts/change-email/", views.change_email, name="change_email"),
    path("accounts/delete-account/", views.delete_account, name="delete_account"),
    path("accounts/password_change/", auth_views.PasswordChangeView.as_view(
        template_name="users/password_change_form.html",
    ), name="password_change"),
    
    path("accounts/password_change/done/", auth_views.PasswordChangeDoneView.as_view(
        template_name="users/password_change_done.html"
    ), name="password_change_done"),
    
    path("accounts/", include("django.contrib.auth.urls")),   
]