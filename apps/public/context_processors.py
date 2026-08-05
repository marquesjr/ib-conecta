from wagtail.models import Site

from apps.public.cms import NEWS_INDEX_SLUG
from apps.public.models import ChurchSettings, NewsIndexPage
from apps.public.whatsapp import build_whatsapp_url


def church_settings(request):
    site = Site.find_for_request(request)
    if site is None:
        site = Site.objects.filter(is_default_site=True).first()

    if site is None:
        return {
            "church_settings": None,
            "whatsapp_url": "",
            "news_index_url": "",
        }

    settings = ChurchSettings.for_site(site)
    news_index = (
        NewsIndexPage.objects.live()
        .public()
        .filter(slug=NEWS_INDEX_SLUG)
        .first()
    )
    return {
        "church_settings": settings,
        "whatsapp_url": build_whatsapp_url(
            settings.whatsapp_number,
            settings.whatsapp_default_message,
        ),
        "news_index_url": news_index.url if news_index else "",
    }
