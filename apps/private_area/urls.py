from django.urls import path

from apps.private_area import views

app_name = "private_area"

urlpatterns = [
    path("area-privada/", views.home, name="home"),
    path("area-privada/documentos/", views.document_library, name="document_library"),
    path(
        "area-privada/documentos/novo/",
        views.document_upload,
        name="document_upload",
    ),
    path(
        "area-privada/documentos/<int:pk>/",
        views.document_download,
        name="document_download",
    ),
]
