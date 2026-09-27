import re

from django import template
from django.conf import settings
from django.utils import timezone
from django.utils.html import format_html

from apps.public.whatsapp import build_whatsapp_share_url, split_whatsapp_welcome

register = template.Library()


@register.filter
def editorial_headline(value):
    """Preserve CMS wording and escape it, emphasizing its final phrase.

    With two or more sentences, the last one goes to its own line and is emphasized
    ("Um lugar para viver a fé. <em>Uma família para caminhar com você.</em>").
    Otherwise the final three words are emphasized.
    """
    value = str(value or "")
    sentences = re.search(r"^(.*[.!?])\s+(\S.*)$", value.strip(), flags=re.S)
    if sentences:
        return format_html("{} <br><em>{}</em>", sentences.group(1), sentences.group(2))
    ending = re.search(r"(\S+(?:\s+\S+){0,2})\s*$", value)
    if not ending:
        return value
    return format_html("{}<em>{}</em>", value[:ending.start()], value[ending.start():])


@register.filter
def hour_label(value):
    """Horário no jeito falado da igreja: ``19h`` ou ``19h30``."""
    if not value:
        return ""
    if timezone.is_aware(value):
        value = timezone.localtime(value)
    return f"{value.hour}h{value.minute:02d}" if value.minute else f"{value.hour}h"


@register.simple_tag
def is_demo_preview():
    return settings.DEBUG and getattr(settings, "EDITORIAL_DEMO_PREVIEW", False)


@register.inclusion_tag("public/_whatsapp_welcome.html")
def whatsapp_welcome(text, part="lead"):
    lead, note = split_whatsapp_welcome(text)
    return {"lead": lead, "note": note, "part": part}


@register.inclusion_tag("public/_whatsapp_share.html", takes_context=True)
def whatsapp_share(context, title="IB Conecta"):
    request = context.get("request")
    share_url = ""
    if request is not None:
        share_url = build_whatsapp_share_url(title, request.build_absolute_uri())
    return {"share_url": share_url}
