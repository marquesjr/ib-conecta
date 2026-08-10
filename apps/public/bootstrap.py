from wagtail.models import Page, Site

from apps.accounts.models import Profile
from apps.public.cms import (
    AGENDA_INDEX_SLUG,
    INSTITUTIONAL_PAGE_SEEDS,
    LIVE_STREAM_SLUG,
    NEWS_INDEX_SLUG,
    SERMON_INDEX_SLUG,
    ensure_cms_editors_group,
    sync_cms_access_for_user,
)
from apps.public.models import (
    EventIndexPage,
    InstitutionalPage,
    LiveStreamPage,
    NewsIndexPage,
    SermonIndexPage,
)


def _site_root() -> Page:
    site = Site.objects.filter(is_default_site=True).first()
    return site.root_page if site else Page.get_first_root_node()


def ensure_news_index() -> NewsIndexPage:
    existing = NewsIndexPage.objects.filter(slug=NEWS_INDEX_SLUG).first()
    if existing:
        return existing

    index = NewsIndexPage(
        title="Notícias",
        slug=NEWS_INDEX_SLUG,
        intro="Comunicados da Igreja Batista em Santa Leopoldina.",
    )
    _site_root().add_child(instance=index)
    index.save_revision().publish()
    return index


def ensure_institutional_pages() -> None:
    root = _site_root()
    for slug, title, intro in INSTITUTIONAL_PAGE_SEEDS:
        if InstitutionalPage.objects.filter(slug=slug).exists():
            continue
        page = InstitutionalPage(
            title=title,
            slug=slug,
            intro=intro,
            body=(
                f"<p>{intro}</p>"
                "<p>Edite este conteúdo no CMS Wagtail quando estiver pronto para publicar a versão final.</p>"
            ),
        )
        root.add_child(instance=page)
        page.save_revision().publish()


def ensure_agenda_index() -> EventIndexPage:
    existing = EventIndexPage.objects.filter(slug=AGENDA_INDEX_SLUG).first()
    if existing:
        return existing

    index = EventIndexPage(
        title="Agenda",
        slug=AGENDA_INDEX_SLUG,
        intro="Cultos e eventos da Igreja Batista em Santa Leopoldina.",
    )
    _site_root().add_child(instance=index)
    index.save_revision().publish()
    return index


def ensure_sermon_index() -> SermonIndexPage:
    existing = SermonIndexPage.objects.filter(slug=SERMON_INDEX_SLUG).first()
    if existing:
        return existing

    index = SermonIndexPage(
        title="Sermões",
        slug=SERMON_INDEX_SLUG,
        intro="Sermões e estudos da Igreja Batista em Santa Leopoldina.",
    )
    _site_root().add_child(instance=index)
    index.save_revision().publish()
    return index


def ensure_live_stream_page() -> LiveStreamPage:
    existing = LiveStreamPage.objects.filter(slug=LIVE_STREAM_SLUG).first()
    if existing:
        return existing

    page = LiveStreamPage(
        title="Ao vivo",
        slug=LIVE_STREAM_SLUG,
        intro="Acompanhe a transmissão quando o culto estiver no ar.",
        body=(
            "<p>Quando houver transmissão, cole a URL do YouTube no CMS Wagtail.</p>"
            "<p>O portal incorpora o player sem hospedar o vídeo.</p>"
        ),
        youtube_url="",
    )
    _site_root().add_child(instance=page)
    page.save_revision().publish()
    return page


def bootstrap_cms() -> None:
    ensure_cms_editors_group()
    ensure_news_index()
    ensure_institutional_pages()
    ensure_agenda_index()
    ensure_sermon_index()
    ensure_live_stream_page()
    for profile in Profile.objects.select_related("user").iterator():
        sync_cms_access_for_user(profile.user)
