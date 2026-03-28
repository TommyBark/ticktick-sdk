"""
Tests for shared model datetime behavior.
"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from ticktick_sdk.models.base import TickTickModel


pytestmark = [pytest.mark.unit]


class TestTickTickModelDatetime:
    """Tests for TickTickModel datetime helpers."""

    def test_format_datetime_v2_normalizes_aware_datetime_to_utc(self) -> None:
        """V2 formatting should preserve the instant by converting to UTC first."""
        dt = datetime(2026, 3, 24, 0, 0, 0, tzinfo=ZoneInfo("Asia/Shanghai"))

        formatted = TickTickModel.format_datetime(dt, "v2")

        assert formatted == "2026-03-23T16:00:00.000+0000"
