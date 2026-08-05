from django.urls import path

from apps.accounts import views

app_name = "accounts"

urlpatterns = [
    path("conta/", views.account_home, name="account_home"),
    path("conta/entrar/", views.login_view, name="login"),
    path("conta/sair/", views.logout_view, name="logout"),
    path("conta/2fa/", views.two_factor_setup, name="two_factor_setup"),
    path("conta/2fa/verificar/", views.two_factor_verify, name="two_factor_verify"),
    path("conta/usuarios/", views.manage_users_demo, name="manage_users_demo"),
    path(
        "conta/recuperar-senha/",
        views.EmailPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "conta/recuperar-senha/enviado/",
        views.EmailPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "conta/redefinir/<uidb64>/<token>/",
        views.EmailPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "conta/redefinir/concluido/",
        views.EmailPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]
