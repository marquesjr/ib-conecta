from django.urls import path

from apps.private_area import ministry_views, views

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
    path("area-privada/ministerios/", ministry_views.ministry_list, name="ministry_list"),
    path(
        "area-privada/ministerios/novo/",
        ministry_views.ministry_create,
        name="ministry_create",
    ),
    path(
        "area-privada/ministerios/<int:pk>/",
        ministry_views.ministry_detail,
        name="ministry_detail",
    ),
    path(
        "area-privada/ministerios/<int:pk>/escalas/nova/",
        ministry_views.schedule_create,
        name="schedule_create",
    ),
    path(
        "area-privada/escalas/<int:pk>/",
        ministry_views.schedule_detail,
        name="schedule_detail",
    ),
    path(
        "area-privada/escalas/<int:pk>/convocar/",
        ministry_views.assignment_add,
        name="assignment_add",
    ),
    path(
        "area-privada/escalas/<int:pk>/calendario/",
        ministry_views.schedule_calendar,
        name="schedule_calendar",
    ),
    path(
        "area-privada/escalas/<int:pk>/imprimir/",
        ministry_views.schedule_print,
        name="schedule_print",
    ),
    path(
        "area-privada/convocacoes/<int:pk>/",
        ministry_views.assignment_respond,
        name="assignment_respond",
    ),
    path(
        "area-privada/convocacoes/<int:pk>/substituir/",
        ministry_views.assignment_substitute,
        name="assignment_substitute",
    ),
]
