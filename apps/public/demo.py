"""Conteúdo de demonstração para revisar o visual do portal no ambiente local."""

from datetime import datetime, time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.utils import timezone
from django.utils.text import slugify
from wagtail.models import Site

from apps.accounts.models import Role
from apps.private_area.models import (
    AssignmentStatus,
    BudgetLineStatus,
    DocumentAudience,
    EventBudgetLine,
    EventChecklistItem,
    EventMaterial,
    EventOperation,
    EventOperationDocument,
    EventSupplier,
    EventTask,
    EventTeam,
    EventTeamMember,
    Ministry,
    MonthlySchedule,
    PlaylistItem,
    PlaylistKind,
    PrivateDocument,
    ScheduleAssignment,
    Song,
    SongReference,
    SongStatus,
    SongVersion,
    Substitution,
    WeeklyPlaylist,
    WORSHIP_FUNCTIONS,
)
from apps.public.bootstrap import bootstrap_cms
from apps.public.cms import (
    AGENDA_INDEX_SLUG,
    INSTITUTIONAL_PAGE_SEEDS,
    LIVE_STREAM_SLUG,
    NEWS_INDEX_SLUG,
    SERMON_INDEX_SLUG,
)
from apps.public.models import (
    ChurchSettings,
    EventFamilyMember,
    EventIndexPage,
    EventPage,
    EventRegistration,
    InstitutionalPage,
    KnowChurchContact,
    LiveStreamPage,
    NewsIndexPage,
    NewsPage,
    PrayerRequest,
    SermonIndexPage,
    SermonPage,
)

User = get_user_model()

DEMO_PASSWORD = "demo-ibconecta"
DEMO_PIX_KEY = "pix-demo@ibconecta.invalid"
DEMO_WHATSAPP = "5527999999999"
DEMO_YOUTUBE = "https://www.youtube.com/watch?v=aqz-KE-bpKQ"
INSTITUTIONAL_PLACEHOLDER = (
    "Edite este conteúdo no CMS Wagtail quando estiver pronto para publicar a versão final."
)
LIVE_PLACEHOLDER = "cole a URL do YouTube no CMS Wagtail"
_MINIMAL_PDF = b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF\n"

DEMO_USERS = (
    ("membro", "Ana", "Souza", Role.MEMBER),
    ("joao", "João", "Pereira", Role.MEMBER),
    ("maria", "Maria", "Oliveira", Role.MEMBER),
    ("carla", "Carla", "Nunes", Role.MEMBER),
    ("lider", "Paulo", "Mendes", Role.MINISTRY_LEADER),
    ("comunicacao", "Lúcia", "Ferreira", Role.COMMUNICATION),
    ("pastor", "Carlos", "Ribeiro", Role.PASTOR),
    ("tesouraria", "Helena", "Dias", Role.TREASURY),
    ("comissao", "Roberto", "Alves", Role.EVENTS_COMMISSION),
)

DEMO_SETTINGS = {
    "evangelistic_headline": "Jesus te convida a conhecer a graça de Deus",
    "evangelistic_message": (
        "A Igreja Batista em Santa Leopoldina celebra a Palavra e acolhe "
        "quem chega da cidade ou da zona rural."
    ),
    "next_service_label": "Culto de celebração",
    "next_service_when": "Domingo, 19h",
    "next_service_description": "Venha participar conosco do próximo culto.",
    "service_times": (
        "Domingo: 9h (escola bíblica) e 19h (culto de celebração)\n"
        "Quarta-feira: 19h30 (estudo bíblico)"
    ),
    "address_line": "Rua do Comércio, Centro, Santa Leopoldina - ES",
    "address_references": "Em frente à praça, próximo ao ponto de ônibus do Centro.",
    "map_url": (
        "https://www.openstreetmap.org/?mlat=-20.1006&mlon=-40.5297#map=16/-20.1006/-40.5297"
    ),
    "accessibility_info": "Entrada pela rampa lateral. Há banco reservado próximo à frente.",
    "transport_info": (
        "Visitantes da zona rural podem combinar carona pelo WhatsApp da igreja "
        "antes do culto de domingo."
    ),
    "whatsapp_number": DEMO_WHATSAPP,
    "whatsapp_default_message": "Olá, gostaria de conversar com a igreja",
    "pix_key": DEMO_PIX_KEY,
    "pix_key_type": ChurchSettings.PixKeyType.EMAIL,
    "pix_beneficiary_name": "Igreja Batista em Santa Leopoldina (demonstração)",
    "pix_city": "Santa Leopoldina",
    "pix_instructions": "Chave de demonstração local. Não envie dinheiro de verdade para este PIX.",
    "instagram_url": "https://instagram.com/ibconecta.demo",
    "facebook_url": "https://facebook.com/ibconecta.demo",
    "youtube_url": "https://youtube.com/@ibconecta.demo",
}

INSTITUTIONAL_BODIES = {
    "historia": (
        "<p>A Igreja Batista em Santa Leopoldina nasceu do desejo de anunciar o "
        "evangelho neste município, com cultos simples e acolhimento a quem chega.</p>"
        "<p>Este texto é semente de demonstração para revisar o layout. A igreja "
        "substitui a história oficial no CMS quando estiver pronta para publicar.</p>"
    ),
    "crencas": (
        "<p>Confessamos a Bíblia como Palavra de Deus, a salvação pela graça mediante "
        "a fé em Jesus Cristo e a vida da igreja em comunhão, oração e missão.</p>"
        "<p>A declaração completa de fé será publicada pela liderança no CMS.</p>"
    ),
    "ministerios": (
        "<p>Há espaço para servir no louvor, na recepção, no ensino das crianças, "
        "na diaconia e no cuidado com quem visita.</p>"
        "<p>Para participar, fale com a liderança após o culto ou pelo WhatsApp da igreja.</p>"
    ),
    "lideranca": (
        "<p>A liderança pastoral e os ministérios servem a igreja local na pregação, "
        "no cuidado e na administração.</p>"
        "<p>Nomes, fotos e contatos oficiais serão publicados no CMS pela igreja.</p>"
    ),
}

LICENSE_TEXT = (
    "Texto original de demonstração do IB Conecta. Autorizado apenas para uso "
    "local de preview no portal."
)


def seed_demo(*, force: bool = False) -> dict[str, int]:
    bootstrap_cms()
    users = _seed_users(force=force)
    settings_changed = _seed_church_settings(force=force)
    public_counts = _seed_public_pages(force=force)
    private_counts = _seed_private_area(users, force=force)
    return {
        "configuracoes": int(settings_changed),
        "usuarios": len(users),
        **public_counts,
        **private_counts,
    }


def _pdf(name: str) -> ContentFile:
    return ContentFile(_MINIMAL_PDF, name=name)


def _next_weekday(weekday: int, hour: int, minute: int = 0, *, weeks: int = 0):
    now = timezone.localtime()
    days = (weekday - now.weekday()) % 7
    if days == 0 and (now.hour, now.minute) >= (hour, minute):
        days = 7
    days += 7 * weeks
    naive = datetime.combine((now + timedelta(days=days)).date(), time(hour, minute))
    return timezone.make_aware(naive, now.tzinfo)


def _backdate(page, days: int) -> None:
    if days <= 0:
        return
    when = timezone.now() - timedelta(days=days)
    type(page).objects.filter(pk=page.pk).update(
        first_published_at=when,
        last_published_at=when,
    )


def _ensure_child(parent, model, slug: str, *, days_ago: int = 0, force: bool = False, **fields):
    existing = model.objects.filter(slug=slug).first()
    if existing:
        if force:
            for key, value in fields.items():
                setattr(existing, key, value)
            existing.save_revision().publish()
        return existing
    page = model(slug=slug, **fields)
    parent.add_child(instance=page)
    page.save_revision().publish()
    _backdate(page, days_ago)
    return page


def _seed_users(*, force: bool) -> dict:
    users = {}
    for username, first_name, last_name, role in DEMO_USERS:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "email": f"{username}@demo.ibconecta.local",
            },
        )
        if created or force:
            user.first_name = first_name
            user.last_name = last_name
            user.email = f"{username}@demo.ibconecta.local"
            user.set_password(DEMO_PASSWORD)
            user.save()
        user.profile.role = role
        user.profile.save()
        users[username] = user
    return users


def _seed_church_settings(*, force: bool) -> bool:
    site = Site.objects.get(is_default_site=True)
    settings = ChurchSettings.for_site(site)
    changed = False
    for field, value in DEMO_SETTINGS.items():
        current = getattr(settings, field)
        default = settings._meta.get_field(field).default
        if callable(default):
            default = default()
        if force or current in ("", default):
            if current != value:
                setattr(settings, field, value)
                changed = True
    if changed:
        settings.save()
    return changed


def _seed_public_pages(*, force: bool) -> dict[str, int]:
    news_index = NewsIndexPage.objects.get(slug=NEWS_INDEX_SLUG)
    event_index = EventIndexPage.objects.get(slug=AGENDA_INDEX_SLUG)
    sermon_index = SermonIndexPage.objects.get(slug=SERMON_INDEX_SLUG)

    news_specs = (
        {
            "slug": "mutirao-limpeza-templo",
            "title": "Mutirão de limpeza do templo",
            "intro": "Sábado pela manhã, para deixar o salão pronto para o culto.",
            "body": (
                "<p>Convidamos as famílias para um mutirão de limpeza e organização "
                "do templo no sábado, das 8h às 11h.</p>"
                "<p>Traga pano e disposição. Haverá café no intervalo.</p>"
            ),
            "days_ago": 3,
        },
        {
            "slug": "tarde-infantil-escola-biblica",
            "title": "Tarde infantil na escola bíblica",
            "intro": "Crianças da igreja e visitantes são bem-vindas no domingo à tarde.",
            "body": (
                "<p>A escola bíblica promove uma tarde de histórias, cânticos e lanche.</p>"
                "<p>Chegue a partir das 14h. Pais podem permanecer no salão.</p>"
            ),
            "days_ago": 10,
        },
        {
            "slug": "oferta-missionaria-do-mes",
            "title": "Oferta missionária deste mês",
            "intro": "A comunicação explica como participar da oferta via PIX da igreja.",
            "body": (
                "<p>Neste mês a oferta missionária apoia o trabalho evangélico na região.</p>"
                "<p>Use a chave PIX da página de contribuições. O portal não processa pagamento.</p>"
            ),
            "days_ago": 18,
        },
        {
            "slug": "culto-acao-de-gracas",
            "title": "Culto de ação de graças",
            "intro": "Um domingo para agradecer em família, com ceia ao final.",
            "body": (
                "<p>No culto de celebração haverá um momento de ação de graças e ceia.</p>"
            ),
            "days_ago": 27,
        },
        {
            "slug": "encontro-jovens-sabado",
            "title": "Encontro de jovens no sábado",
            "intro": "Conversa, louvor e lanche no salão, a partir das 19h.",
            "body": "<p>Amigos da escola e da vizinhança são bem-vindos.</p>",
            "days_ago": 40,
        },
    )
    for spec in news_specs:
        days_ago = spec.pop("days_ago")
        _ensure_child(news_index, NewsPage, days_ago=days_ago, force=force, **spec)

    sunday = _next_weekday(6, 19)
    sunday_morning = _next_weekday(6, 9)
    wednesday = _next_weekday(2, 19, 30)
    saturday = _next_weekday(5, 16)
    couples = _next_weekday(6, 19, weeks=2)
    retreat_start = _next_weekday(5, 17, weeks=3)

    event_specs = (
        {
            "slug": "culto-celebracao",
            "title": "Culto de celebração",
            "starts_at": sunday,
            "ends_at": sunday + timedelta(hours=2),
            "location": "Templo — Santa Leopoldina",
            "body": "<p>Culto de celebração com pregação, oração e louvor. Entrada livre.</p>",
            "requires_registration": False,
            "is_retreat": False,
        },
        {
            "slug": "escola-biblica",
            "title": "Escola bíblica dominical",
            "starts_at": sunday_morning,
            "ends_at": sunday_morning + timedelta(hours=1, minutes=15),
            "location": "Salão da igreja",
            "body": "<p>Classes para crianças, jovens e adultos antes do culto da noite.</p>",
            "requires_registration": False,
            "is_retreat": False,
        },
        {
            "slug": "estudo-biblico",
            "title": "Estudo bíblico",
            "starts_at": wednesday,
            "ends_at": wednesday + timedelta(hours=1, minutes=30),
            "location": "Templo — Santa Leopoldina",
            "body": "<p>Estudo aberto a visitantes. Traga sua Bíblia, se tiver.</p>",
            "requires_registration": False,
            "is_retreat": False,
        },
        {
            "slug": "encontro-casais",
            "title": "Encontro de casais",
            "starts_at": couples,
            "ends_at": couples + timedelta(hours=3),
            "location": "Salão da igreja",
            "body": "<p>Noite de Palavra e jantar simples. Inscrição necessária para o lanche.</p>",
            "requires_registration": True,
            "is_retreat": False,
        },
        {
            "slug": "evangelismo-praca",
            "title": "Evangelismo na praça",
            "starts_at": saturday,
            "ends_at": saturday + timedelta(hours=2),
            "location": "Praça do Centro",
            "body": "<p>Distribuição de convites na praça. Encontro no templo às 15h30.</p>",
            "requires_registration": False,
            "is_retreat": False,
        },
        {
            "slug": "retiro-familias",
            "title": "Retiro de famílias",
            "starts_at": retreat_start,
            "ends_at": retreat_start + timedelta(days=2, hours=2),
            "location": "Sítio da igreja, zona rural de Santa Leopoldina",
            "body": "<p>Retiro familiar com cultos, recreação e convivência. Inscrição no formulário.</p>",
            "requires_registration": True,
            "is_retreat": True,
            "capacity": 8,
            "sensitive_retain_days": 30,
        },
    )
    events = {}
    for spec in event_specs:
        events[spec["slug"]] = _ensure_child(event_index, EventPage, force=force, **spec)

    sermon_specs = (
        {
            "slug": "a-graca-que-nos-alcanca",
            "title": "A graça que nos alcança",
            "intro": "Estudo de João 1, para leitura e reflexão.",
            "body": (
                "<p>A graça de Deus não espera mérito: ela nos alcança e nos convida a crer em Cristo.</p>"
                "<p>Conteúdo de demonstração para o portal — substitua pelo sermão publicado no CMS.</p>"
            ),
            "media_url": DEMO_YOUTUBE,
            "days_ago": 7,
        },
        {
            "slug": "o-senhor-e-o-meu-pastor",
            "title": "O Senhor é o meu pastor",
            "intro": "Meditação no Salmo 23.",
            "body": "<p>O cuidado do Senhor sustenta o rebanho no vale e no pasto.</p>",
            "media_url": DEMO_YOUTUBE,
            "days_ago": 14,
        },
        {
            "slug": "andar-em-novidade-de-vida",
            "title": "Andar em novidade de vida",
            "intro": "Leitura de Romanos 6, sem mídia incorporada.",
            "body": "<p>A nova vida em Cristo se mostra no cotidiano, não só no culto.</p>",
            "media_url": "",
            "days_ago": 21,
        },
        {
            "slug": "fe-que-se-ve-nas-obras",
            "title": "Fé que se vê nas obras",
            "intro": "Estudo de Tiago 2.",
            "body": "<p>A fé que salva não fica só no discurso: ela se vê no cuidado com o próximo.</p>",
            "media_url": DEMO_YOUTUBE,
            "days_ago": 28,
        },
    )
    for spec in sermon_specs:
        days_ago = spec.pop("days_ago")
        _ensure_child(sermon_index, SermonPage, days_ago=days_ago, force=force, **spec)

    live = LiveStreamPage.objects.get(slug=LIVE_STREAM_SLUG)
    if force or not live.youtube_url or LIVE_PLACEHOLDER in live.body:
        live.intro = "Quando o culto estiver no ar, a transmissão aparece aqui."
        live.body = (
            "<p>O portal incorpora o player do YouTube sem autoplay e sem hospedar o vídeo.</p>"
            "<p>O vídeo abaixo é apenas para testar o layout da página ao vivo.</p>"
        )
        live.youtube_url = DEMO_YOUTUBE
        live.save_revision().publish()

    for slug, _title, intro in INSTITUTIONAL_PAGE_SEEDS:
        page = InstitutionalPage.objects.filter(slug=slug).first()
        if not page:
            continue
        if force or INSTITUTIONAL_PLACEHOLDER in page.body:
            page.intro = intro
            page.body = INSTITUTIONAL_BODIES.get(slug, f"<p>{intro}</p>")
            page.save_revision().publish()

    _seed_public_inbox(events, force=force)
    return {
        "noticias": len(news_specs),
        "eventos": len(event_specs),
        "sermoes": len(sermon_specs),
    }


def _seed_public_inbox(events: dict, *, force: bool) -> None:
    couples = events["encontro-casais"]
    retreat = events["retiro-familias"]

    if force or not EventRegistration.objects.filter(event=couples).exists():
        EventRegistration.objects.filter(event=couples).delete()
        EventRegistration.objects.create(
            event=couples,
            name="Marcos e Juliana Prado",
            email="casal.prado@demo.ibconecta.local",
            phone="27999990001",
            lgpd_consent=True,
            status=EventRegistration.Status.CONFIRMED,
        )
        EventRegistration.objects.create(
            event=couples,
            name="Ricardo Alves",
            email="ricardo.alves@demo.ibconecta.local",
            phone="27999990002",
            lgpd_consent=True,
            status=EventRegistration.Status.CONFIRMED,
        )

    if force or not EventRegistration.objects.filter(event=retreat).exists():
        EventRegistration.objects.filter(event=retreat).delete()
        family = EventRegistration.objects.create(
            event=retreat,
            name="Fernanda Lima",
            email="fernanda.lima@demo.ibconecta.local",
            phone="27988880001",
            birth_date="1986-04-12",
            emergency_name="Paulo Lima",
            emergency_phone="27988880000",
            dietary_restrictions="sem glúten (demonstração)",
            medical_notes="alergia a amendoim (dado de demonstração)",
            transport_needed=True,
            boarding_point="Praça do Centro",
            accommodation="quarto família",
            pix_status=EventRegistration.PixStatus.PAID,
            lgpd_consent=True,
            status=EventRegistration.Status.CONFIRMED,
            checked_in_at=timezone.now() - timedelta(days=1),
        )
        EventFamilyMember.objects.create(
            registration=family,
            name="Paulo Lima",
            birth_date="1984-09-03",
            is_minor=False,
        )
        EventFamilyMember.objects.create(
            registration=family,
            name="Helena Lima",
            birth_date="2014-02-20",
            is_minor=True,
            dietary_restrictions="sem lactose (demonstração)",
        )
        EventFamilyMember.objects.create(
            registration=family,
            name="Pedro Lima",
            birth_date="2017-11-08",
            is_minor=True,
        )
        EventRegistration.objects.create(
            event=retreat,
            name="Sônia Castro",
            email="sonia.castro@demo.ibconecta.local",
            phone="27988880003",
            birth_date="1990-01-15",
            emergency_name="Igor Castro",
            emergency_phone="27988880004",
            pix_status=EventRegistration.PixStatus.PENDING,
            lgpd_consent=True,
            status=EventRegistration.Status.CONFIRMED,
        )
        EventRegistration.objects.create(
            event=retreat,
            name="Igor Castro",
            email="igor.castro@demo.ibconecta.local",
            phone="27988880004",
            birth_date="1988-07-22",
            emergency_name="Sônia Castro",
            emergency_phone="27988880003",
            pix_status=EventRegistration.PixStatus.PENDING,
            lgpd_consent=True,
            status=EventRegistration.Status.CONFIRMED,
        )
        EventRegistration.objects.create(
            event=retreat,
            name="Família Rocha (lista de espera)",
            email="rocha@demo.ibconecta.local",
            phone="27988880009",
            birth_date="1982-03-30",
            emergency_name="Carla Rocha",
            emergency_phone="27988880010",
            transport_needed=True,
            boarding_point="Ponto da rodoviária",
            pix_status=EventRegistration.PixStatus.PENDING,
            lgpd_consent=True,
            status=EventRegistration.Status.WAITLISTED,
        )

    if force or not PrayerRequest.objects.exists():
        PrayerRequest.objects.all().delete()
        PrayerRequest.objects.create(
            is_anonymous=True,
            body="Peço oração pela saúde da minha mãe, em tratamento (pedido de demonstração).",
            lgpd_consent=True,
            status=PrayerRequest.Status.NEW,
        )
        PrayerRequest.objects.create(
            is_anonymous=False,
            name="Teresa Gomes",
            email="teresa@demo.ibconecta.local",
            phone="27977770001",
            body="Oração por emprego e ânimo para a família (pedido de demonstração).",
            lgpd_consent=True,
            status=PrayerRequest.Status.IN_PROGRESS,
        )
        PrayerRequest.objects.create(
            is_anonymous=False,
            name="Nilson Pires",
            email="nilson@demo.ibconecta.local",
            body="Agradecimento pela visita pastoral da semana passada (demonstração).",
            lgpd_consent=True,
            status=PrayerRequest.Status.DONE,
        )

    if force or not KnowChurchContact.objects.exists():
        KnowChurchContact.objects.all().delete()
        KnowChurchContact.objects.create(
            name="Beatriz Ramos",
            email="beatriz@demo.ibconecta.local",
            phone="27966660001",
            message="Moro na zona rural e gostaria de saber o horário do culto de domingo.",
            lgpd_consent=True,
            status=KnowChurchContact.Status.NEW,
        )
        KnowChurchContact.objects.create(
            name="Eduardo Martins",
            email="eduardo@demo.ibconecta.local",
            message="Quero conhecer a igreja. Posso ir com meus dois filhos?",
            lgpd_consent=True,
            status=KnowChurchContact.Status.IN_PROGRESS,
        )


def _seed_private_area(users: dict, *, force: bool) -> dict[str, int]:
    comunicacao = users["comunicacao"]
    lider = users["lider"]
    tesouraria = users["tesouraria"]
    comissao = users["comissao"]
    membro = users["membro"]

    docs = (
        ("Comunicado aos membros", DocumentAudience.MEMBERS, "Aviso interno de demonstração."),
        ("Pauta da comunicação", DocumentAudience.CONTENT, "Pauta restrita à comunicação e ao pastor."),
        ("Relatório da tesouraria", DocumentAudience.FINANCES, "Demonstração para o perfil de tesouraria."),
        ("Ata da administração", DocumentAudience.ADMIN, "Ata fictícia visível só à administração."),
    )
    created_docs = 0
    for title, audience, description in docs:
        if PrivateDocument.objects.filter(title=title).exists() and not force:
            continue
        if force:
            PrivateDocument.objects.filter(title=title).delete()
        doc = PrivateDocument(
            title=title,
            description=description,
            audience=audience,
            created_by=comunicacao,
        )
        doc.file.save(f"{slugify(title)}.pdf", _pdf(f"{slugify(title)}.pdf"), save=True)
        created_docs += 1

    louvor, _ = Ministry.objects.get_or_create(
        name="Louvor",
        defaults={"description": "Cânticos, instrumentos e projeção.", "created_by": lider},
    )
    Ministry.objects.get_or_create(
        name="Recepção",
        defaults={"description": "Acolhida na porta e na nave.", "created_by": lider},
    )
    Ministry.objects.get_or_create(
        name="Infantil",
        defaults={"description": "Crianças na escola bíblica e no culto.", "created_by": lider},
    )
    Ministry.objects.get_or_create(
        name="Diaconia",
        defaults={"description": "Cuidado prático com a igreja e visitantes.", "created_by": lider},
    )

    now = timezone.localtime()
    schedule, _ = MonthlySchedule.objects.get_or_create(
        ministry=louvor,
        year=now.year,
        month=now.month,
        defaults={"notes": "Escala de demonstração do mês corrente.", "created_by": lider},
    )
    if force or not schedule.assignments.exists():
        schedule.assignments.all().delete()
        sunday = _next_weekday(6, 19)
        previous = sunday - timedelta(days=7)
        participants = [membro, users["joao"], users["maria"], users["carla"], lider]
        for offset, starts in enumerate((previous, sunday)):
            for function, participant in zip(WORSHIP_FUNCTIONS, participants):
                status = AssignmentStatus.CONFIRMED if offset == 0 else AssignmentStatus.PENDING
                ScheduleAssignment.objects.create(
                    schedule=schedule,
                    starts_at=starts,
                    function=function,
                    participant=participant,
                    status=status,
                )
        sonoplastia = schedule.assignments.filter(function="Sonoplastia", starts_at=previous).first()
        if sonoplastia:
            Substitution.objects.get_or_create(
                assignment=sonoplastia,
                replaced=users["carla"],
                substitute=users["joao"],
                defaults={"created_by": lider},
            )

    song_specs = (
        {
            "title": "Graça à beira do rio",
            "key": "G",
            "tempo": "76 BPM",
            "tags": "adoração, original",
            "lyrics": (
                "A graça encontrou o vale\n"
                "e o rio cantou louvor.\n"
                "Quem tinha sede bebeu da fonte\n"
                "e descansou no Senhor."
            ),
            "chords": "G          D\nA graça encontrou o vale\nC          G\ne o rio cantou louvor.",
            "status": SongStatus.PUBLISHED,
        },
        {
            "title": "O vale canta",
            "key": "D",
            "tempo": "82 BPM",
            "tags": "celebração",
            "lyrics": (
                "O vale canta ao amanhecer\n"
                "Santa Leopoldina vai louvar.\n"
                "O Senhor guardou o semeador\n"
                "e a colheita vai chegar."
            ),
            "chords": "D       A\nO vale canta ao amanhecer",
            "status": SongStatus.PUBLISHED,
        },
        {
            "title": "Firme no Senhor",
            "key": "A",
            "tempo": "90 BPM",
            "tags": "confiança",
            "lyrics": (
                "Firme no Senhor, mesmo no sereno\n"
                "caminho a igreja até Sião.\n"
                "Não tememos a noite do ribeiro:\n"
                "Cristo é nossa porção."
            ),
            "chords": "A      E\nFirme no Senhor, mesmo no sereno",
            "status": SongStatus.PUBLISHED,
        },
        {
            "title": "Paz na colina",
            "key": "C",
            "tempo": "70 BPM",
            "tags": "encerramento",
            "lyrics": (
                "Há paz na colina ao anoitecer\n"
                "quando o povo ora em um só coração.\n"
                "A lâmpada acesa no templo pequeno\n"
                "lembra que o Senhor é o pão."
            ),
            "chords": "C      G\nHá paz na colina ao anoitecer",
            "status": SongStatus.PUBLISHED,
        },
        {
            "title": "Rascunho de ensaio",
            "key": "E",
            "tempo": "88 BPM",
            "tags": "rascunho",
            "lyrics": "Letra ainda em revisão para o ensaio da equipe.",
            "chords": "E  B  C#m  A",
            "status": SongStatus.DRAFT,
        },
    )
    songs = []
    for spec in song_specs:
        slug = slugify(spec["title"])
        defaults = {
            "title": spec["title"],
            "status": spec["status"],
            "key": spec["key"],
            "tempo": spec["tempo"],
            "lyrics": spec["lyrics"],
            "chords": spec["chords"],
            "tags": spec["tags"],
            "authors": "Texto original de demonstração IB Conecta",
            "source": "Material interno de preview",
            "license": LICENSE_TEXT,
            "permitted_uses": "Ensaio e culto de demonstração no portal local.",
            "authorized": True,
            "created_by": lider,
            "published_at": timezone.now() if spec["status"] == SongStatus.PUBLISHED else None,
        }
        song, created = Song.objects.get_or_create(slug=slug, defaults=defaults)
        if force and not created:
            for key, value in defaults.items():
                setattr(song, key, value)
            song.save()
        if not song.references.exists():
            SongReference.objects.create(
                song=song,
                label="Áudio de referência (demonstração)",
                target_url=DEMO_YOUTUBE,
            )
        if song.status == SongStatus.PUBLISHED and not song.versions.exists():
            SongVersion.objects.create(
                song=song,
                name="Congregacional",
                key=song.key,
                lyrics=song.lyrics,
                chords=song.chords,
            )
        if song.status == SongStatus.PUBLISHED and not song.score:
            song.score.save(f"{slug}.pdf", _pdf(f"{slug}.pdf"), save=True)
        songs.append(song)

    published = [song for song in songs if song.status == SongStatus.PUBLISHED]
    service, _ = WeeklyPlaylist.objects.get_or_create(
        ministry=louvor,
        kind=PlaylistKind.SERVICE,
        starts_at=_next_weekday(6, 19),
        defaults={"notes": "Abertura do culto de celebração.", "created_by": lider},
    )
    rehearsal, _ = WeeklyPlaylist.objects.get_or_create(
        ministry=louvor,
        kind=PlaylistKind.REHEARSAL,
        starts_at=_next_weekday(5, 19),
        defaults={"notes": "Ensaio da equipe de louvor.", "created_by": lider},
    )
    if not service.items.exists():
        for position, song in enumerate(published[:4], start=1):
            PlaylistItem.objects.create(
                playlist=service,
                song=song,
                version=song.versions.first(),
                position=position,
                key=song.key,
                notes="Começar mais baixo" if position == 1 else "",
            )
    if not rehearsal.items.exists() and published:
        PlaylistItem.objects.create(
            playlist=rehearsal,
            song=published[0],
            version=published[0].versions.first(),
            position=1,
            key=published[0].key,
        )

    retreat = EventPage.objects.filter(slug="retiro-familias").first()
    couples = EventPage.objects.filter(slug="encontro-casais").first()
    if retreat:
        operation, _ = EventOperation.objects.get_or_create(
            public_event=retreat,
            defaults={
                "notes": "Programação: culto sexta 20h, recreação sábado, encerramento domingo 10h.",
                "created_by": comissao,
            },
        )
        kitchen, _ = EventTeam.objects.get_or_create(operation=operation, name="Cozinha")
        reception, _ = EventTeam.objects.get_or_create(operation=operation, name="Recepção")
        EventTeamMember.objects.get_or_create(team=kitchen, user=users["maria"])
        EventTeamMember.objects.get_or_create(team=reception, user=membro)
        EventTeamMember.objects.get_or_create(team=reception, user=users["joao"])
        EventTask.objects.get_or_create(
            operation=operation,
            title="Confirmar ônibus da zona rural",
            defaults={"assignee": membro, "done": False},
        )
        EventTask.objects.get_or_create(
            operation=operation,
            title="Montar escala de cozinha",
            defaults={"assignee": users["maria"], "done": True},
        )
        EventChecklistItem.objects.get_or_create(
            operation=operation,
            label="Kit de primeiros socorros",
            defaults={"assignee": users["joao"], "done": False},
        )
        EventSupplier.objects.get_or_create(
            operation=operation,
            name="Transporte Vale do Santa",
            defaults={"contact": "27 99999-1010", "notes": "Van para 12 pessoas."},
        )
        EventMaterial.objects.get_or_create(
            operation=operation,
            name="Colchões extras",
            defaults={"quantity": "8", "notes": "Retirar no depósito da igreja."},
        )
        EventBudgetLine.objects.get_or_create(
            operation=operation,
            description="Alimentação do retiro",
            defaults={
                "amount": Decimal("850.00"),
                "status": BudgetLineStatus.APPROVED,
                "created_by": comissao,
                "reviewed_by": tesouraria,
            },
        )
        EventBudgetLine.objects.get_or_create(
            operation=operation,
            description="Combustível da van",
            defaults={
                "amount": Decimal("220.00"),
                "status": BudgetLineStatus.PENDING,
                "created_by": comissao,
            },
        )
        if not operation.documents.exists():
            document = EventOperationDocument(
                operation=operation,
                title="Programação do retiro",
                created_by=comissao,
            )
            document.file.save(
                "programacao-retiro.pdf",
                _pdf("programacao-retiro.pdf"),
                save=True,
            )
    if couples:
        EventOperation.objects.get_or_create(
            public_event=couples,
            defaults={
                "notes": "Decoração simples, jantar no salão e palco pequeno para o louvor.",
                "created_by": comissao,
            },
        )

    return {
        "documentos": created_docs or PrivateDocument.objects.count(),
        "louvores": len(songs),
    }
