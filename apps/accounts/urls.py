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
        "conta/eventos/inscritos/",
        views.event_registrations,
        name="event_registrations",
    ),
    path(
        "conta/eventos/inscritos/<int:pk>/cancelar/",
        views.event_registration_cancel,
        name="event_registration_cancel",
    ),
    path("conta/pedidos-de-oracao/", views.prayer_requests, name="prayer_requests"),
    path(
        "conta/pedidos-de-oracao/<int:pk>/situacao/",
        views.prayer_request_status,
        name="prayer_request_status",
    ),
    path(
        "conta/quero-conhecer/",
        views.know_church_contacts,
        name="know_church_contacts",
    ),
    path(
        "conta/quero-conhecer/<int:pk>/situacao/",
        views.know_church_contact_status,
        name="know_church_contact_status",
    ),
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
