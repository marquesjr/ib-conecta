from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from wagtail.models import Site

from apps.public.forms import KnowChurchForm, PrayerRequestForm
from apps.public.models import ChurchSettings, KnowChurchContact, PrayerRequest
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
    return render(request, "public/home.html")


def plan_visit(request):
    return render(request, "public/plan_visit.html")


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
