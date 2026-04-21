from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('2fa/verify/', views.verify_2fa, name='verify_2fa'),

    path("accounts/register/", views.register_user, name="register"),
    path("accounts/verify/", views.verify_code, name="verify_code"),

    path("accounts/password_reset/", views.password_reset_request, name="password_reset"),
    path("accounts/password_reset/verify/", views.password_reset_verify, name="password_reset_verify"),
    path("accounts/password_reset/confirm/", views.password_reset_new_password, name="password_reset_new_password"),
    path("accounts/reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name="users/password_reset_complete.html"
    ), name="password_reset_complete"),

    path("accounts/logout/", auth_views.LogoutView.as_view(template_name="users/logout.html"), name="logout"),
    path("accounts/profile/", views.profile, name="profile"),
    path("accounts/change-email/", views.change_email, name="change_email"),
    path("accounts/delete-account/", views.delete_account, name="delete_account"),

    path("accounts/unsubscribe/", views.unsubscribe_newsletter, name="unsubscribe_newsletter"),
    path("accounts/subscribe/", views.subscribe_newsletter, name="subscribe_newsletter"),

    path("accounts/redeem/", views.redeem_code_view, name="redeem_code"),
    path("accounts/resend-verification-code/", views.resend_verification_code, name="resend_verification_code"),

    path("accounts/password_change/", auth_views.PasswordChangeView.as_view(
        template_name="users/password_change_form.html",
    ), name="password_change"),

    path("accounts/password_change/done/", auth_views.PasswordChangeDoneView.as_view(
        template_name="users/password_change_done.html"
    ), name="password_change_done"),
    
    path('accounts/order/<int:order_id>/invoice/', views.order_invoice, name='order_invoice'),

]