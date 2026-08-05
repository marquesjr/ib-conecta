from wagtail.models import Site

from apps.public.models import ChurchSettings
from apps.public.whatsapp import build_whatsapp_url


def church_settings(request):
    site = Site.find_for_request(request)
    if site is None:
        site = Site.objects.filter(is_default_site=True).first()

    if site is None:
        return {
            "church_settings": None,
            "whatsapp_url": "",
        }

    settings = ChurchSettings.for_site(site)
    return {
        "church_settings": settings,
        "whatsapp_url": build_whatsapp_url(
            settings.whatsapp_number,
            settings.whatsapp_default_message,
        ),
    }
