from datetime import timedelta

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
from wagtail.snippets.models import register_snippet


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
    is_retreat = models.BooleanField(
        default=False,
        verbose_name="É retiro",
        help_text="Usa inscrição familiar, transporte, PIX e check-in na área privada.",
    )
    capacity = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Vagas",
        help_text="Conta pessoas (titular + familiares). Sem valor, não há lista de espera.",
    )
    sensitive_retain_days = models.PositiveIntegerField(
        default=30,
        verbose_name="Dias para descarte de dados sensíveis",
        help_text="Após o término do retiro, dados médicos e de menores são descartados.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("starts_at"),
        FieldPanel("ends_at"),
        FieldPanel("location"),
        FieldPanel("body"),
        FieldPanel("requires_registration"),
        FieldPanel("is_retreat"),
        FieldPanel("capacity"),
        FieldPanel("sensitive_retain_days"),
    ]

    parent_page_types = ["public.EventIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"

    def get_context(self, request, *args, **kwargs):
        from apps.public.forms import EventRegistrationForm, FamilyMemberFormSet, RetreatRegistrationForm

        context = super().get_context(request, *args, **kwargs)
        if self.is_retreat:
            context["registration_form"] = RetreatRegistrationForm()
            context["family_formset"] = FamilyMemberFormSet(prefix="family")
        else:
            context["registration_form"] = EventRegistrationForm()
        return context

    @path("inscrever/")
    def register_view(self, request):
        from apps.public.forms import EventRegistrationForm, FamilyMemberFormSet, RetreatRegistrationForm
        from apps.public.retreats import create_retreat_registration

        if not self.requires_registration:
            return HttpResponse(status=404)

        if request.method != "POST":
            return redirect(self.url)

        if self.is_retreat:
            form = RetreatRegistrationForm(request.POST, event=self)
            formset = FamilyMemberFormSet(request.POST, prefix="family")
            if form.is_valid() and formset.is_valid():
                form.require_guardian_if_minors(formset, self)
            if form.is_valid() and formset.is_valid():
                registration = create_retreat_registration(self, form, formset)
                if registration.status == EventRegistration.Status.WAITLISTED:
                    messages.success(
                        request,
                        f"Inscrição na lista de espera. Obrigado, {form.cleaned_data['name']}!",
                    )
                else:
                    messages.success(
                        request,
                        f"Inscrição confirmada. Obrigado, {form.cleaned_data['name']}!",
                    )
                return redirect(self.url)
            return self.render(
                request,
                context_overrides={
                    "registration_form": form,
                    "family_formset": formset,
                },
            )

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
        WAITLISTED = "waitlisted", "Lista de espera"
        CANCELLED = "cancelled", "Cancelada"

    class PixStatus(models.TextChoices):
        PENDING = "pending", "PIX pendente"
        PAID = "paid", "PIX pago"
        WAIVED = "waived", "Isento"

    event = models.ForeignKey(
        EventPage,
        on_delete=models.CASCADE,
        related_name="registrations",
        verbose_name="Evento",
    )
    name = models.CharField(max_length=120, verbose_name="Nome")
    email = models.EmailField(verbose_name="E-mail")
    phone = models.CharField(max_length=30, blank=True, default="", verbose_name="Telefone")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Data de nascimento")
    is_minor = models.BooleanField(default=False, verbose_name="Menor de idade")
    guardian_name = models.CharField(
        max_length=120,
        blank=True,
        default="",
        verbose_name="Responsável legal",
    )
    guardian_phone = models.CharField(
        max_length=30,
        blank=True,
        default="",
        verbose_name="Telefone do responsável",
    )
    guardian_relationship = models.CharField(
        max_length=80,
        blank=True,
        default="",
        verbose_name="Parentesco do responsável",
    )
    emergency_name = models.CharField(
        max_length=120,
        blank=True,
        default="",
        verbose_name="Contato de emergência",
    )
    emergency_phone = models.CharField(
        max_length=30,
        blank=True,
        default="",
        verbose_name="Telefone de emergência",
    )
    dietary_restrictions = models.TextField(
        blank=True,
        default="",
        verbose_name="Restrições alimentares",
    )
    medical_notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Informações médicas",
    )
    transport_needed = models.BooleanField(default=False, verbose_name="Precisa de transporte")
    boarding_point = models.CharField(
        max_length=120,
        blank=True,
        default="",
        verbose_name="Ponto de embarque",
    )
    accommodation = models.CharField(
        max_length=120,
        blank=True,
        default="",
        verbose_name="Acomodação",
    )
    pix_status = models.CharField(
        max_length=20,
        choices=PixStatus.choices,
        blank=True,
        default="",
        verbose_name="Status do PIX",
    )
    checked_in_at = models.DateTimeField(blank=True, null=True, verbose_name="Check-in")
    lgpd_consent = models.BooleanField(default=False, verbose_name="Consentimento LGPD")
    sensitive_discarded_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Dados sensíveis descartados em",
    )
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

    def party_size(self) -> int:
        return 1 + self.family_members.count()


class EventFamilyMember(models.Model):
    registration = models.ForeignKey(
        EventRegistration,
        on_delete=models.CASCADE,
        related_name="family_members",
        verbose_name="Inscrição",
    )
    name = models.CharField(max_length=120, verbose_name="Nome")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Data de nascimento")
    is_minor = models.BooleanField(default=False, verbose_name="Menor de idade")
    dietary_restrictions = models.TextField(
        blank=True,
        default="",
        verbose_name="Restrições alimentares",
    )
    medical_notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Informações médicas",
    )
    checked_in_at = models.DateTimeField(blank=True, null=True, verbose_name="Check-in")

    class Meta:
        ordering = ["name"]
        verbose_name = "Familiar inscrito"
        verbose_name_plural = "Familiares inscritos"

    def __str__(self) -> str:
        return self.name


class PrayerRequest(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Novo"
        IN_PROGRESS = "in_progress", "Em acompanhamento"
        DONE = "done", "Concluído"

    is_anonymous = models.BooleanField(default=False, verbose_name="Anônimo")
    name = models.CharField(max_length=120, blank=True, default="", verbose_name="Nome")
    email = models.EmailField(blank=True, default="", verbose_name="E-mail")
    phone = models.CharField(max_length=30, blank=True, default="", verbose_name="Telefone")
    body = models.TextField(verbose_name="Pedido")
    lgpd_consent = models.BooleanField(default=False, verbose_name="Consentimento LGPD")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name="Situação",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Pedido de oração"
        verbose_name_plural = "Pedidos de oração"

    def __str__(self) -> str:
        who = "Anônimo" if self.is_anonymous else (self.name or "Sem nome")
        return f"{who} ({self.get_status_display()})"


class KnowChurchContact(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Novo"
        IN_PROGRESS = "in_progress", "Em acompanhamento"
        DONE = "done", "Concluído"

    name = models.CharField(max_length=120, verbose_name="Nome")
    email = models.EmailField(blank=True, default="", verbose_name="E-mail")
    phone = models.CharField(max_length=30, blank=True, default="", verbose_name="Telefone")
    message = models.TextField(blank=True, default="", verbose_name="Mensagem")
    lgpd_consent = models.BooleanField(verbose_name="Consentimento LGPD")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name="Situação",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contato Quero conhecer"
        verbose_name_plural = "Contatos Quero conhecer"

    def __str__(self) -> str:
        return f"{self.name} ({self.get_status_display()})"


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

    class PixKeyType(models.TextChoices):
        RANDOM = "random", "Chave aleatória"
        EMAIL = "email", "E-mail"
        PHONE = "phone", "Telefone"
        CPF = "cpf", "CPF"
        CNPJ = "cnpj", "CNPJ"

    pix_key = models.CharField(
        max_length=140,
        blank=True,
        default="",
        verbose_name="Chave PIX",
        help_text="Chave PIX da igreja. Não cadastre dados bancários de terceiros.",
    )
    pix_key_type = models.CharField(
        max_length=20,
        blank=True,
        default="",
        choices=PixKeyType.choices,
        verbose_name="Tipo da chave PIX",
    )
    pix_beneficiary_name = models.CharField(
        max_length=140,
        blank=True,
        default="",
        verbose_name="Nome do favorecido",
    )
    pix_city = models.CharField(
        max_length=80,
        blank=True,
        default="",
        verbose_name="Cidade do PIX",
    )
    pix_instructions = models.TextField(
        blank=True,
        default="",
        verbose_name="Orientação para ofertas",
        help_text="Texto público. O portal não processa pagamento nem guarda dados do doador.",
    )
    instagram_url = models.URLField(
        blank=True,
        default="",
        verbose_name="Instagram",
    )
    facebook_url = models.URLField(
        blank=True,
        default="",
        verbose_name="Facebook",
    )
    youtube_url = models.URLField(
        blank=True,
        default="",
        verbose_name="YouTube",
    )

    class InstagramMode(models.TextChoices):
        OFF = "off", "Desligado — usar apenas a galeria curada"
        INSTAGRAM_LOGIN = "instagram_login", "Login Empresarial do Instagram (conta Criador ou Empresa, sem Página)"
        FACEBOOK_LOGIN = "facebook_login", "Login do Facebook (conta Empresa ligada a uma Página)"

    instagram_handle = models.CharField(
        max_length=60,
        blank=True,
        default="",
        verbose_name="Arroba do Instagram",
        help_text="Sem o @. Ex.: igrejabatista.santaleopoldina",
    )
    instagram_mode = models.CharField(
        max_length=20,
        default=InstagramMode.OFF,
        choices=InstagramMode.choices,
        verbose_name="Origem do acervo",
        help_text=(
            "A API oficial exige conta Profissional (Criador ou Empresa). "
            "Conta pessoal não tem acesso a nenhuma API oficial."
        ),
    )
    instagram_user_id = models.CharField(
        max_length=40,
        blank=True,
        default="",
        verbose_name="ID da conta do Instagram",
        help_text="Necessário apenas no Login do Facebook. O token é cadastrado fora desta tela.",
    )
    archive_frame_count = models.PositiveSmallIntegerField(
        default=12,
        verbose_name="Quadros no acervo da home",
        help_text="Quantas fotografias a folha de contato exibe.",
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
        MultiFieldPanel(
            [
                FieldPanel("pix_key"),
                FieldPanel("pix_key_type"),
                FieldPanel("pix_beneficiary_name"),
                FieldPanel("pix_city"),
                FieldPanel("pix_instructions"),
            ],
            heading="Contribuições PIX",
        ),
        MultiFieldPanel(
            [
                FieldPanel("instagram_url"),
                FieldPanel("facebook_url"),
                FieldPanel("youtube_url"),
            ],
            heading="Redes sociais",
        ),
        MultiFieldPanel(
            [
                FieldPanel("instagram_handle"),
                FieldPanel("instagram_mode"),
                FieldPanel("instagram_user_id"),
                FieldPanel("archive_frame_count"),
            ],
            heading="Acervo do Instagram",
        ),
    ]

    class Meta:
        verbose_name = "Configurações da igreja"

    def social_links(self):
        links = []
        for label, url in (
            ("Instagram", self.instagram_url),
            ("Facebook", self.facebook_url),
            ("YouTube", self.youtube_url),
        ):
            if url:
                links.append({"label": label, "url": url})
        return links


@register_snippet
class ArchiveFrame(models.Model):
    """Uma fotografia da folha de contato — vinda da API do Instagram ou curada no CMS.

    A imagem é guardada localmente porque as URLs do CDN da Meta expiram, e nesta
    superfície a fotografia é o material principal: imagem quebrada seria a falha
    mais visível da página.
    """

    class Source(models.TextChoices):
        INSTAGRAM = "instagram", "Instagram"
        CURATED = "curated", "Curado no CMS"

    source = models.CharField(
        max_length=20,
        default=Source.CURATED,
        choices=Source.choices,
        verbose_name="Origem",
    )
    remote_id = models.CharField(
        max_length=80,
        blank=True,
        default="",
        verbose_name="ID no Instagram",
        help_text="Preenchido pela sincronização. Deixe vazio em quadros curados.",
    )
    image = models.ImageField(
        upload_to="archive/",
        verbose_name="Fotografia",
    )
    alt_text = models.CharField(
        max_length=250,
        blank=True,
        default="",
        verbose_name="Descrição para leitor de tela",
        help_text="Descreva a cena. Sem isso a fotografia fica inacessível.",
    )
    caption = models.CharField(
        max_length=120,
        blank=True,
        default="",
        verbose_name="Legenda",
        help_text="Legenda curta, escrita como anotação a nanquim sob o quadro.",
    )
    permalink = models.URLField(
        blank=True,
        default="",
        verbose_name="Link do post",
    )
    taken_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Data",
    )
    is_visible = models.BooleanField(
        default=True,
        verbose_name="Exibir no site",
    )

    panels = [
        FieldPanel("image"),
        FieldPanel("alt_text"),
        FieldPanel("caption"),
        FieldPanel("permalink"),
        FieldPanel("taken_at"),
        FieldPanel("is_visible"),
    ]

    class Meta:
        ordering = ["-taken_at", "-pk"]
        verbose_name = "Quadro do acervo"
        verbose_name_plural = "Quadros do acervo"
        constraints = [
            models.UniqueConstraint(
                fields=["remote_id"],
                condition=models.Q(source="instagram"),
                name="unique_instagram_remote_id",
            )
        ]

    def __str__(self):
        return self.caption or f"Quadro {self.pk}"


class InstagramCredential(models.Model):
    """Token de longa duração da API do Instagram, guardado fora do painel de configurações.

    Fica num modelo próprio para que o segredo não apareça na tela que a comunicação
    usa no dia a dia, e para que a renovação programada possa reescrevê-lo — o que um
    token só em variável de ambiente não permitiria, deixando o acervo morrer a cada
    60 dias sem aviso.
    """

    access_token = models.TextField(verbose_name="Token de acesso")
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Expira em",
    )
    refreshed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Renovado em",
    )
    last_sync_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Última sincronização",
    )
    last_sync_error = models.TextField(
        blank=True,
        default="",
        verbose_name="Último erro de sincronização",
    )

    class Meta:
        verbose_name = "Credencial do Instagram"
        verbose_name_plural = "Credenciais do Instagram"

    def __str__(self):
        return "Credencial do Instagram"

    @classmethod
    def current(cls):
        return cls.objects.order_by("pk").first()

    def is_expiring(self, within_days=10):
        if not self.expires_at:
            return True
        return self.expires_at - timezone.now() <= timedelta(days=within_days)
