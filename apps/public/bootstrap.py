from wagtail.models import Page, Site

from apps.accounts.models import Profile
from apps.public.cms import (
    INSTITUTIONAL_PAGE_SEEDS,
    NEWS_INDEX_SLUG,
    ensure_cms_editors_group,
    sync_cms_access_for_user,
)
from apps.public.models import InstitutionalPage, NewsIndexPage


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


def bootstrap_cms() -> None:
    ensure_cms_editors_group()
    ensure_news_index()
    ensure_institutional_pages()
    for profile in Profile.objects.select_related("user").iterator():
        sync_cms_access_for_user(profile.user)
