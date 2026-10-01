from datetime import datetime
from zoneinfo import ZoneInfo

from django.test import SimpleTestCase
from django.utils import timezone

from apps.public.templatetags.public_tags import long_date, long_datetime, short_datetime

TZ = ZoneInfo("America/Sao_Paulo")


class DateFilterTests(SimpleTestCase):
    def test_short_datetime_drops_the_year_in_the_current_one(self):
        year = timezone.localdate().year
        value = datetime(year, 10, 24, 17, 0, tzinfo=TZ)
        self.assertNotIn(str(year), short_datetime(value))
        self.assertTrue(short_datetime(value).endswith("· 17h"))

    def test_short_datetime_keeps_other_years_and_minutes(self):
        self.assertEqual(short_datetime(datetime(2020, 1, 4, 19, 30, tzinfo=TZ)), "sáb, 4 jan 2020 · 19h30")

    def test_detail_formats(self):
        value = datetime(2026, 10, 24, 17, 0, tzinfo=TZ)
        self.assertEqual(long_datetime(value), "Sábado, 24 de outubro de 2026 · 17h")
        self.assertEqual(long_date(value), "24 de outubro de 2026")

    def test_empty_values(self):
        self.assertEqual(short_datetime(None), "")
        self.assertEqual(long_date(None), "")
        self.assertEqual(long_datetime(None), "")
