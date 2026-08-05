from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import RichTextField
from wagtail.models import Page


class InstitutionalPage(Page):
    """Página institucional editável (história, crenças, ministérios, liderança)."""

    intro = models.CharField(
        max_length=300,
        blank=True,
        default="",
        verbose_name="Resumo",
        help_text="Frase curta exibida abaixo do título.",
    )
    body = RichTextField(verbose_name="Conteúdo")

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
    ]

    parent_page_types = ["wagtailcore.Page"]
    subpage_types = []

    class Meta:
        verbose_name = "Página institucional"
        verbose_name_plural = "Páginas institucionais"


class NewsIndexPage(Page):
    """Índice público de notícias e comunicados."""

    intro = models.CharField(
        max_length=300,
        blank=True,
        default="",
        verbose_name="Resumo",
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["public.NewsPage"]

    class Meta:
        verbose_name = "Índice de notícias"
        verbose_name_plural = "Índices de notícias"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["news_pages"] = (
            NewsPage.objects.child_of(self).live().public().order_by("-first_published_at", "-path")
        )
        return context


class NewsPage(Page):
    """Notícia ou comunicado publicado pela Comunicação."""

    intro = models.CharField(
        max_length=300,
        blank=True,
        default="",
        verbose_name="Resumo",
    )
    body = RichTextField(verbose_name="Conteúdo")

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
    ]

    parent_page_types = ["public.NewsIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = "Notícia"
        verbose_name_plural = "Notícias"


@register_setting
class ChurchSettings(BaseSiteSetting):
    evangelistic_headline = models.CharField(
        max_length=200,
        default="Boas-novas para Santa Leopoldina",
        verbose_name="Título evangelístico",
    )
    evangelistic_message = models.TextField(
        default=(
            "A Igreja Batista em Santa Leopoldina anuncia a Palavra de Deus "
            "e convida você a participar dos cultos."
        ),
        verbose_name="Mensagem da home",
    )
    next_service_label = models.CharField(
        max_length=120,
        default="Próximo culto",
        verbose_name="Nome do próximo culto",
    )
    next_service_when = models.CharField(
        max_length=120,
        default="Consulte os horários",
        verbose_name="Quando é o próximo culto",
    )
    next_service_description = models.TextField(
        blank=True,
        default="Venha participar conosco.",
        verbose_name="Detalhes do próximo culto",
    )

    service_times = models.TextField(
        default="Domingo às 19h",
        verbose_name="Horários de culto",
    )
    address_line = models.CharField(
        max_length=255,
        default="Santa Leopoldina - ES",
        verbose_name="Endereço",
    )
    address_references = models.TextField(
        blank=True,
        default="",
        verbose_name="Pontos de referência",
    )
    map_url = models.URLField(
        blank=True,
        default="",
        verbose_name="Link do mapa",
        help_text="Preferir link externo leve (Google Maps / OSM), sem incorporação pesada.",
    )
    accessibility_info = models.TextField(
        blank=True,
        default="",
        verbose_name="Acessibilidade",
    )
    transport_info = models.TextField(
        blank=True,
        default="",
        verbose_name="Transporte e caronas",
        help_text="Inclua orientações para visitantes da zona rural.",
    )

    whatsapp_number = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name="WhatsApp (somente dígitos, com DDI)",
        help_text="Ex.: 5527999999999",
    )
    whatsapp_default_message = models.CharField(
        max_length=300,
        default="Olá, gostaria de conversar com a igreja",
        verbose_name="Mensagem inicial do WhatsApp",
    )
    whatsapp_welcome_text = models.TextField(
        default=(
            "Fale conosco pelo WhatsApp para dúvidas, conversa, desabafo ou pedido de oração. "
            "Responderemos assim que possível — não é um canal de plantão 24 horas."
        ),
        verbose_name="Texto de acolhimento do WhatsApp",
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("evangelistic_headline"),
                FieldPanel("evangelistic_message"),
                FieldPanel("next_service_label"),
                FieldPanel("next_service_when"),
                FieldPanel("next_service_description"),
            ],
            heading="Home evangelística",
        ),
        MultiFieldPanel(
            [
                FieldPanel("service_times"),
                FieldPanel("address_line"),
                FieldPanel("address_references"),
                FieldPanel("map_url"),
                FieldPanel("accessibility_info"),
                FieldPanel("transport_info"),
            ],
            heading="Planeje sua visita",
        ),
        MultiFieldPanel(
            [
                FieldPanel("whatsapp_number"),
                FieldPanel("whatsapp_default_message"),
                FieldPanel("whatsapp_welcome_text"),
            ],
            heading="WhatsApp institucional",
        ),
    ]

    class Meta:
        verbose_name = "Configurações da igreja"
