import datetime

from django.db import migrations

SUNDAY = 6
SUNDAY_EVENTS = [
    ("Escola Bíblica Dominical", datetime.time(9, 0)),
    ("Culto de Adoração ao Senhor", datetime.time(19, 0)),
]


def seed_sunday_events(apps, schema_editor):
    RecurringEvent = apps.get_model("public", "RecurringEvent")
    for title, starts_at in SUNDAY_EVENTS:
        RecurringEvent.objects.get_or_create(
            title=title,
            defaults={"weekday": SUNDAY, "starts_at": starts_at},
        )


def remove_sunday_events(apps, schema_editor):
    RecurringEvent = apps.get_model("public", "RecurringEvent")
    RecurringEvent.objects.filter(title__in=[title for title, _ in SUNDAY_EVENTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("public", "0019_recurring_event"),
    ]

    operations = [
        migrations.RunPython(seed_sunday_events, remove_sunday_events),
    ]
