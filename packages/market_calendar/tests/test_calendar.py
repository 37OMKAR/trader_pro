"""
Unit tests for the Indian Market Calendar Engine.
"""

from datetime import datetime, date, time
import pytest
from packages.shared_types.market_types import MarketSessionStatus
from packages.market_calendar.calendar import (
    IndianMarketCalendar,
    IST_TIMEZONE,
    MARKET_OPEN,
    MARKET_CLOSE,
)


def test_holiday_detection():
    calendar = IndianMarketCalendar()
    # Republic Day 2025-01-26 (Sunday) / 2026-01-26 (Monday)
    is_hol_26, name_26 = calendar.is_holiday(date(2026, 1, 26))
    assert is_hol_26 is True
    assert "Republic Day" in name_26

    # Independence Day 2025-08-15
    is_hol_15, name_15 = calendar.is_holiday(date(2025, 8, 15))
    assert is_hol_15 is True
    assert "Independence Day" in name_15

    # Regular day (e.g. Wednesday 2025-01-15)
    is_hol_norm, _ = calendar.is_holiday(date(2025, 1, 15))
    assert is_hol_norm is False


def test_weekend_detection():
    calendar = IndianMarketCalendar()
    # 2025-01-18 is Saturday, 2025-01-19 is Sunday
    assert calendar.is_weekend(date(2025, 1, 18)) is True
    assert calendar.is_weekend(date(2025, 1, 19)) is True
    # 2025-01-20 is Monday
    assert calendar.is_weekend(date(2025, 1, 20)) is False


def test_session_status():
    calendar = IndianMarketCalendar()
    
    # 1. Regular market hours on a Tuesday (2025-01-14 at 10:30 IST)
    dt_open = IST_TIMEZONE.localize(datetime(2025, 1, 14, 10, 30, 0))
    status, name = calendar.get_session_status(dt_open)
    assert status == MarketSessionStatus.OPEN
    assert "Regular Market Hours" in name

    # 2. Pre-open session (2025-01-14 at 09:05 IST)
    dt_pre = IST_TIMEZONE.localize(datetime(2025, 1, 14, 9, 5, 0))
    status, name = calendar.get_session_status(dt_pre)
    assert status == MarketSessionStatus.PRE_OPEN

    # 3. Post-close session (2025-01-14 at 15:45 IST)
    dt_post = IST_TIMEZONE.localize(datetime(2025, 1, 14, 15, 45, 0))
    status, name = calendar.get_session_status(dt_post)
    assert status == MarketSessionStatus.POST_CLOSE

    # 4. Night closed (2025-01-14 at 22:00 IST)
    dt_night = IST_TIMEZONE.localize(datetime(2025, 1, 14, 22, 0, 0))
    status, name = calendar.get_session_status(dt_night)
    assert status == MarketSessionStatus.CLOSED

    # 5. Weekend closed
    dt_sat = IST_TIMEZONE.localize(datetime(2025, 1, 18, 11, 0, 0))
    status, name = calendar.get_session_status(dt_sat)
    assert status == MarketSessionStatus.WEEKEND


def test_expiry_date_calculation():
    calendar = IndianMarketCalendar()
    # Monthly expiry for January 2025 (Last Thursday is Jan 30, 2025)
    exp_jan_2025 = calendar.get_monthly_expiry(2025, 1)
    assert exp_jan_2025 == date(2025, 1, 30)

    # Monthly expiry for August 2025 (Last Thursday is Aug 28, 2025)
    exp_aug_2025 = calendar.get_monthly_expiry(2025, 8)
    assert exp_aug_2025 == date(2025, 8, 28)
