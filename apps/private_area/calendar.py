from datetime import timedelta

from django.utils import timezone


def build_schedule_ics(schedule, request=None) -> str:
    tz_name = timezone.get_current_timezone_name()
    stamp = timezone.localtime(timezone.now())
    url = ""
    if request is not None:
        url = request.build_absolute_uri()

    def fmt(dt):
        return timezone.localtime(dt).strftime("%Y%m%dT%H%M%S")

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//IB Conecta//Escalas//PT",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]
    assignments = schedule.assignments.select_related("participant", "schedule__ministry")
    for assignment in assignments:
        summary = f"{schedule.ministry.name} — {assignment.function}"
        ends = assignment.starts_at + timedelta(hours=2)
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:schedule-{schedule.pk}-assignment-{assignment.pk}@ibsantaleopoldina.com.br",
                f"DTSTAMP;TZID={tz_name}:{fmt(stamp)}",
                f"DTSTART;TZID={tz_name}:{fmt(assignment.starts_at)}",
                f"DTEND;TZID={tz_name}:{fmt(ends)}",
                f"SUMMARY:{_escape_ics(summary)}",
            ]
        )
        description = assignment.participant.username
        if description:
            lines.append(f"DESCRIPTION:{_escape_ics(description)}")
        if url:
            lines.append(f"URL:{url}")
        lines.append("END:VEVENT")
    lines.extend(["END:VCALENDAR", ""])
    return "\r\n".join(lines)


def build_playlist_ics(playlist, request=None) -> str:
    tz_name = timezone.get_current_timezone_name()
    stamp = timezone.localtime(timezone.now())
    url = ""
    if request is not None:
        url = request.build_absolute_uri()

    def fmt(dt):
        return timezone.localtime(dt).strftime("%Y%m%dT%H%M%S")

    summary = f"{playlist.ministry.name} — {playlist.get_kind_display()}"
    songs = []
    for item in playlist.items.select_related("song"):
        title = item.song.title
        key = item.display_key()
        if key:
            songs.append(f"{item.position}. {title} (Tom {key})")
        else:
            songs.append(f"{item.position}. {title}")
    description = "\n".join(songs)
    ends = playlist.starts_at + timedelta(hours=2)
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//IB Conecta//Playlists//PT",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
        f"UID:playlist-{playlist.pk}@ibsantaleopoldina.com.br",
        f"DTSTAMP;TZID={tz_name}:{fmt(stamp)}",
        f"DTSTART;TZID={tz_name}:{fmt(playlist.starts_at)}",
        f"DTEND;TZID={tz_name}:{fmt(ends)}",
        f"SUMMARY:{_escape_ics(summary)}",
    ]
    if description:
        lines.append(f"DESCRIPTION:{_escape_ics(description)}")
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
