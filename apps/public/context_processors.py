from wagtail.models import Site

from apps.public.cms import (
    AGENDA_INDEX_SLUG,
    LIVE_STREAM_SLUG,
    NEWS_INDEX_SLUG,
    SERMON_INDEX_SLUG,
)
from apps.public.models import (
    ChurchSettings,
    EventIndexPage,
    LiveStreamPage,
    NewsIndexPage,
    SermonIndexPage,
)
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
            "agenda_index_url": "",
            "sermon_index_url": "",
            "live_stream_url": "",
        }

    settings = ChurchSettings.for_site(site)
    news_index = (
        NewsIndexPage.objects.live()
        .public()
        .filter(slug=NEWS_INDEX_SLUG)
        .first()
    )
    agenda_index = (
        EventIndexPage.objects.live()
        .public()
        .filter(slug=AGENDA_INDEX_SLUG)
        .first()
    )
    sermon_index = (
        SermonIndexPage.objects.live()
        .public()
        .filter(slug=SERMON_INDEX_SLUG)
        .first()
    )
    live_stream = (
        LiveStreamPage.objects.live()
        .public()
        .filter(slug=LIVE_STREAM_SLUG)
        .first()
    )
    return {
        "church_settings": settings,
        "whatsapp_url": build_whatsapp_url(
            settings.whatsapp_number,
            settings.whatsapp_default_message,
        ),
        "news_index_url": news_index.url if news_index else "",
        "agenda_index_url": agenda_index.url if agenda_index else "",
        "sermon_index_url": sermon_index.url if sermon_index else "",
        "live_stream_url": live_stream.url if live_stream else "",
    }
