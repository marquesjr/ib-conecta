from django import template

from apps.public.whatsapp import build_whatsapp_share_url

register = template.Library()


@register.inclusion_tag("public/_whatsapp_share.html", takes_context=True)
def whatsapp_share(context, title="IB Conecta"):
    request = context.get("request")
    share_url = ""
    if request is not None:
        share_url = build_whatsapp_share_url(title, request.build_absolute_uri())
    return {"share_url": share_url}
