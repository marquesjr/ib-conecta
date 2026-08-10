from django.utils import timezone


def build_event_ics(event, request=None) -> str:
    """Build a minimal VEVENT iCalendar document for an EventPage."""
    tz_name = timezone.get_current_timezone_name()
    starts = timezone.localtime(event.starts_at)
    ends = timezone.localtime(event.ends_at) if event.ends_at else starts
    stamp = timezone.localtime(timezone.now())
    uid = f"event-{event.pk}@ibsantaleopoldina.com.br"
    url = ""
    if request is not None:
        url = request.build_absolute_uri(event.url)
    elif event.url:
        url = event.url

    def fmt(dt):
        return dt.strftime("%Y%m%dT%H%M%S")

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//IB Conecta//Agenda//PT",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP;TZID={tz_name}:{fmt(stamp)}",
        f"DTSTART;TZID={tz_name}:{fmt(starts)}",
        f"DTEND;TZID={tz_name}:{fmt(ends)}",
        f"SUMMARY:{_escape_ics(event.title)}",
    ]
    if event.location:
        lines.append(f"LOCATION:{_escape_ics(event.location)}")
    if url:
        lines.append(f"URL:{url}")
    lines.extend(["END:VEVENT", "END:VCALENDAR", ""])
    return "\r\n".join(lines)


def _escape_ics(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )
