import re

from django import template
from django.conf import settings
from django.utils.html import format_html

from apps.public.whatsapp import build_whatsapp_share_url, split_whatsapp_welcome

register = template.Library()


@register.filter
def editorial_headline(value):
    """Preserve CMS wording and escape it, emphasizing its final phrase."""
    value = str(value or "")
    ending = re.search(r"(\S+(?:\s+\S+){0,2})\s*$", value)
    if not ending:
        return value
    return format_html("{}<em>{}</em>", value[:ending.start()], value[ending.start():])


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
