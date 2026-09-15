import unittest
from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from backup_layout import (  # noqa: E402
    DAILY_RETENTION_DAYS,
    MONTHLY_RETENTION_DAYS,
    artifact_filename,
    daily_key,
    monthly_key,
    monthly_prefix,
)


class BackupLayoutTests(unittest.TestCase):
    def setUp(self) -> None:
        self.stamp = datetime(2026, 9, 15, 16, 45, 0, tzinfo=timezone.utc)

    def test_artifact_filename_is_utc_stamp(self) -> None:
        self.assertEqual(
            artifact_filename(self.stamp),
            "ib-conecta-20260915T164500Z.tar.age",
        )

    def test_daily_key_uses_date_prefix(self) -> None:
        self.assertEqual(
            daily_key(self.stamp),
            "daily/2026-09-15/ib-conecta-20260915T164500Z.tar.age",
        )

    def test_monthly_key_uses_year_month_prefix(self) -> None:
        self.assertEqual(monthly_prefix(self.stamp), "monthly/2026-09/")
        self.assertEqual(
            monthly_key(self.stamp),
            "monthly/2026-09/ib-conecta-20260915T164500Z.tar.age",
        )

    def test_retention_matches_documented_policy(self) -> None:
        self.assertEqual(DAILY_RETENTION_DAYS, 30)
        self.assertEqual(MONTHLY_RETENTION_DAYS, 366)


if __name__ == "__main__":
    unittest.main()
