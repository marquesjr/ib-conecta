from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail import urls as wagtail_urls

urlpatterns = [
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("", include("apps.accounts.urls")),
    path("", include("apps.private_area.urls")),
    path("", include("apps.public.urls")),
    path("", include(wagtail_urls)),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
