from datetime import date, timedelta

from django.utils import timezone

from apps.public.models import EventFamilyMember, EventRegistration

MINOR_AGE = 18


def as_local_date(value) -> date:
    if timezone.is_aware(value):
        return timezone.localtime(value).date()
    return value.date()


def age_on(birth_date: date, on_date: date) -> int:
    years = on_date.year - birth_date.year
    if (on_date.month, on_date.day) < (birth_date.month, birth_date.day):
        years -= 1
    return years


def is_minor(birth_date: date | None, on_date: date) -> bool:
    if birth_date is None:
        return False
    return age_on(birth_date, on_date) < MINOR_AGE


def event_reference_date(event) -> date:
    moment = event.ends_at or event.starts_at
    return as_local_date(moment)


def sensitive_retain_until(event) -> date:
    return event_reference_date(event) + timedelta(days=event.sensitive_retain_days)


def occupancy(event) -> int:
    confirmed = EventRegistration.objects.filter(
        event=event,
        status=EventRegistration.Status.CONFIRMED,
    )
    people = confirmed.count()
    people += EventFamilyMember.objects.filter(registration__in=confirmed).count()
    return people


def incoming_party(form, formset) -> list[dict]:
    members = []
    for child in formset:
        data = child.cleaned_data
        if data.get("name"):
            members.append(data)
    return members


def create_retreat_registration(event, form, formset) -> EventRegistration:
    members = incoming_party(form, formset)
    on_date = event_reference_date(event)
    primary_minor = is_minor(form.cleaned_data.get("birth_date"), on_date)
    party = 1 + len(members)
    status = EventRegistration.Status.CONFIRMED
    if event.capacity is not None and occupancy(event) + party > event.capacity:
        status = EventRegistration.Status.WAITLISTED
    registration = EventRegistration.objects.create(
        event=event,
        name=form.cleaned_data["name"],
        email=form.cleaned_data["email"],
        phone=form.cleaned_data.get("phone") or "",
        birth_date=form.cleaned_data.get("birth_date"),
        is_minor=primary_minor,
        guardian_name=form.cleaned_data.get("guardian_name") or "",
        guardian_phone=form.cleaned_data.get("guardian_phone") or "",
        guardian_relationship=form.cleaned_data.get("guardian_relationship") or "",
        emergency_name=form.cleaned_data.get("emergency_name") or "",
        emergency_phone=form.cleaned_data.get("emergency_phone") or "",
        dietary_restrictions=form.cleaned_data.get("dietary_restrictions") or "",
        medical_notes=form.cleaned_data.get("medical_notes") or "",
        transport_needed=bool(form.cleaned_data.get("transport_needed")),
        boarding_point=form.cleaned_data.get("boarding_point") or "",
        accommodation=form.cleaned_data.get("accommodation") or "",
        pix_status=EventRegistration.PixStatus.PENDING,
        lgpd_consent=True,
        status=status,
    )
    for member in members:
        EventFamilyMember.objects.create(
            registration=registration,
            name=member["name"],
            birth_date=member.get("birth_date"),
            is_minor=is_minor(member.get("birth_date"), on_date),
            dietary_restrictions=member.get("dietary_restrictions") or "",
            medical_notes=member.get("medical_notes") or "",
        )
    return registration


def discard_sensitive_fields(registration: EventRegistration) -> bool:
    if registration.sensitive_discarded_at:
        return False
    registration.dietary_restrictions = ""
    registration.medical_notes = ""
    registration.guardian_name = ""
    registration.guardian_phone = ""
    registration.guardian_relationship = ""
    if registration.is_minor:
        registration.birth_date = None
    registration.sensitive_discarded_at = timezone.now()
    registration.save(
        update_fields=[
            "dietary_restrictions",
            "medical_notes",
            "guardian_name",
            "guardian_phone",
            "guardian_relationship",
            "birth_date",
            "sensitive_discarded_at",
        ]
    )
    for member in registration.family_members.all():
        member.dietary_restrictions = ""
        member.medical_notes = ""
        if member.is_minor:
            member.birth_date = None
        member.save(
            update_fields=["dietary_restrictions", "medical_notes", "birth_date"]
        )
    return True


def discard_due_retreat_sensitive_data(*, today: date | None = None) -> int:
    today = today or timezone.localdate()
    discarded = 0
    qs = EventRegistration.objects.filter(
        event__is_retreat=True,
        sensitive_discarded_at__isnull=True,
    ).select_related("event")
    for registration in qs:
        if sensitive_retain_until(registration.event) <= today:
            if discard_sensitive_fields(registration):
                discarded += 1
    return discarded
