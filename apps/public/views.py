from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from wagtail.models import Site

from apps.public.archive import archive_frames
from apps.public.forms import KnowChurchForm, PrayerRequestForm
from apps.public.models import (
    ChurchSettings,
    EventPage,
    KnowChurchContact,
    NewsPage,
    PrayerRequest,
    SermonPage,
)
from apps.public.privacy import (
    DEFAULT_RETREAT_SENSITIVE_RETAIN_DAYS,
    EVENT_REGISTRATION_RETENTION_DAYS,
    INBOX_RETENTION_MONTHS,
)
from apps.public.spam import RATE_LIMIT_MESSAGE, honeypot_triggered, is_rate_limited
from apps.public.whatsapp import build_whatsapp_url


def _form_whatsapp_url(request, message: str) -> str:
    site = Site.find_for_request(request)
    if site is None:
        site = Site.objects.filter(is_default_site=True).first()
    if site is None:
        return ""
    settings = ChurchSettings.for_site(site)
    return build_whatsapp_url(settings.whatsapp_number, message)


def _submit_or_reject_spam(request, form, *, scope: str, success_url: str, success_message: str, model):
    if honeypot_triggered(request.POST):
        messages.success(request, success_message)
        return redirect(success_url)
    if is_rate_limited(request, scope):
        messages.error(request, RATE_LIMIT_MESSAGE)
        return None
    if form.is_valid():
        model.objects.create(**form.submission_payload())
        messages.success(request, success_message)
        return redirect(success_url)
    return None


def home(request):
    """Convite editorial, fotografia em destaque e conteúdo publicado da igreja."""
    site = Site.find_for_request(request) or Site.objects.filter(is_default_site=True).first()
    count = ChurchSettings.for_site(site).archive_frame_count if site else 12
    frames = archive_frames(count)

    return render(
        request,
        "public/home.html",
        {
            "archive_frames": frames,
            # Imagem gerada não pode passar por prova: a home diz quando o acervo é de exemplo.
            "archive_is_seeded": any(frame["synthetic"] for frame in frames),
            "upcoming_events": EventPage.objects.live()
            .public()
            .filter(starts_at__gte=timezone.now())
            .order_by("starts_at")[:3],
            "recent_sermons": SermonPage.objects.live()
            .public()
            .order_by("-first_published_at")[:3],
            "recent_news": NewsPage.objects.live()
            .public()
            .order_by("-first_published_at")[:3],
        },
    )


def plan_visit(request):
    return render(request, "public/plan_visit.html")


def contribute(request):
    return render(request, "public/contribute.html")


def privacy(request):
    return render(
        request,
        "public/privacy.html",
        {
            "default_retreat_retain_days": DEFAULT_RETREAT_SENSITIVE_RETAIN_DAYS,
            "inbox_retention_months": INBOX_RETENTION_MONTHS,
            "event_registration_retention_days": EVENT_REGISTRATION_RETENTION_DAYS,
        },
    )


@require_http_methods(["GET", "POST"])
def prayer_request(request):
    form = PrayerRequestForm(request.POST or None)
    if request.method == "POST":
        response = _submit_or_reject_spam(
            request,
            form,
            scope="prayer",
            success_url="prayer_request",
            success_message=(
                "Pedido de oração recebido. A equipe pastoral irá orar com confidencialidade."
            ),
            model=PrayerRequest,
        )
        if response is not None:
            return response
    return render(
        request,
        "public/prayer_request.html",
        {
            "form": form,
            "form_whatsapp_url": _form_whatsapp_url(
                request,
                "Olá, gostaria de deixar um pedido de oração",
            ),
        },
    )


@require_http_methods(["GET", "POST"])
def know_church(request):
    form = KnowChurchForm(request.POST or None)
    if request.method == "POST":
        response = _submit_or_reject_spam(
            request,
            form,
            scope="know_church",
            success_url="know_church",
            success_message="Recebemos seu contato. A igreja falará com você em breve.",
            model=KnowChurchContact,
        )
        if response is not None:
            return response
    return render(
        request,
        "public/know_church.html",
        {
            "form": form,
            "form_whatsapp_url": _form_whatsapp_url(
                request,
                "Olá, quero conhecer a igreja",
            ),
        },
    )
