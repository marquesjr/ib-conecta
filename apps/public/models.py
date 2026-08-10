from django.contrib import messages
from django.db import models
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, path
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


class EventIndexPage(Page):
    """Índice público da agenda de cultos e eventos."""

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
    subpage_types = ["public.EventPage"]

    class Meta:
        verbose_name = "Índice da agenda"
        verbose_name_plural = "Índices da agenda"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["event_pages"] = (
            EventPage.objects.child_of(self)
            .live()
            .public()
            .filter(starts_at__gte=timezone.now())
            .order_by("starts_at", "path")
        )
        return context


class EventPage(RoutablePageMixin, Page):
    """Culto ou evento público da agenda."""

    starts_at = models.DateTimeField(verbose_name="Início")
    ends_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Término",
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Local",
    )
    body = RichTextField(blank=True, default="", verbose_name="Descrição")
    requires_registration = models.BooleanField(
        default=False,
        verbose_name="Exige inscrição",
    )

    content_panels = Page.content_panels + [
        FieldPanel("starts_at"),
        FieldPanel("ends_at"),
        FieldPanel("location"),
        FieldPanel("body"),
        FieldPanel("requires_registration"),
    ]

    parent_page_types = ["public.EventIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"

    def get_context(self, request, *args, **kwargs):
        from apps.public.forms import EventRegistrationForm

        context = super().get_context(request, *args, **kwargs)
        context["registration_form"] = EventRegistrationForm()
        return context

    @path("inscrever/")
    def register_view(self, request):
        from apps.public.forms import EventRegistrationForm

        if not self.requires_registration:
            return HttpResponse(status=404)

        if request.method != "POST":
            return redirect(self.url)

        form = EventRegistrationForm(request.POST)
        if form.is_valid():
            EventRegistration.objects.create(
                event=self,
                name=form.cleaned_data["name"],
                email=form.cleaned_data["email"],
                phone=form.cleaned_data.get("phone", ""),
            )
            messages.success(
                request,
                f"Inscrição confirmada. Obrigado, {form.cleaned_data['name']}!",
            )
            return redirect(self.url)

        return self.render(
            request,
            context_overrides={"registration_form": form},
        )

    @path("calendario/")
    def calendar_ics(self, request):
        from apps.public.calendar import build_event_ics

        content = build_event_ics(self, request)
        response = HttpResponse(content, content_type="text/calendar; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="{self.slug}.ics"'
        return response


class EventRegistration(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = "confirmed", "Confirmada"
        CANCELLED = "cancelled", "Cancelada"

    event = models.ForeignKey(
        EventPage,
        on_delete=models.CASCADE,
        related_name="registrations",
        verbose_name="Evento",
    )
    name = models.CharField(max_length=120, verbose_name="Nome")
    email = models.EmailField(verbose_name="E-mail")
    phone = models.CharField(max_length=30, blank=True, default="", verbose_name="Telefone")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CONFIRMED,
        verbose_name="Situação",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Inscrição em evento"
        verbose_name_plural = "Inscrições em eventos"

    def __str__(self) -> str:
        return f"{self.name} → {self.event}"


class SermonIndexPage(Page):
    """Índice público de sermões e estudos."""

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
    subpage_types = ["public.SermonPage"]

    class Meta:
        verbose_name = "Índice de sermões"
        verbose_name_plural = "Índices de sermões"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["sermon_pages"] = (
            SermonPage.objects.child_of(self)
            .live()
            .public()
            .order_by("-first_published_at", "-path")
        )
        return context


class SermonPage(Page):
    """Sermão ou estudo com texto e mídia incorporada externa (sem upload de vídeo)."""

    intro = models.CharField(
        max_length=300,
        blank=True,
        default="",
        verbose_name="Resumo",
    )
    body = RichTextField(blank=True, default="", verbose_name="Conteúdo")
    media_url = models.URLField(
        blank=True,
        default="",
        verbose_name="URL da mídia incorporada",
        help_text="YouTube ou outro link externo. Não use upload de vídeo no portal.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
        FieldPanel("media_url"),
    ]

    parent_page_types = ["public.SermonIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = "Sermão"
        verbose_name_plural = "Sermões"

    def get_context(self, request, *args, **kwargs):
        from apps.public.embeds import is_external_audio_url, youtube_embed_src

        context = super().get_context(request, *args, **kwargs)
        context["media_embed_src"] = youtube_embed_src(self.media_url)
        context["media_is_audio"] = is_external_audio_url(self.media_url)
        return context


class LiveStreamPage(Page):
    """Página de transmissão ao vivo com incorporação YouTube."""

    intro = models.CharField(
        max_length=300,
        blank=True,
        default="",
        verbose_name="Resumo",
    )
    body = RichTextField(blank=True, default="", verbose_name="Conteúdo")
    youtube_url = models.URLField(
        blank=True,
        default="",
        verbose_name="URL do YouTube ao vivo",
        help_text="Link do vídeo ou transmissão no YouTube. Sem autoplay agressivo.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
        FieldPanel("youtube_url"),
    ]

    parent_page_types = ["wagtailcore.Page"]
    subpage_types = []

    class Meta:
        verbose_name = "Transmissão ao vivo"
        verbose_name_plural = "Transmissões ao vivo"

    def get_context(self, request, *args, **kwargs):
        from apps.public.embeds import youtube_embed_src

        context = super().get_context(request, *args, **kwargs)
        context["live_embed_src"] = youtube_embed_src(self.youtube_url)
        return context


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
