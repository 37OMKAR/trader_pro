"""
Market AI — Indian Market Trading Calendar Engine
Handles Asia/Kolkata (IST) exchange sessions, NSE/BSE holidays,
special sessions (e.g. Muhurat Trading), and F&O expiry schedules.
"""

from datetime import datetime, date, time, timedelta
from typing import Dict, List, Optional, Tuple
import pytz
from packages.shared_types.market_types import MarketSessionStatus


IST_TIMEZONE = pytz.timezone("Asia/Kolkata")

# Standard Indian Trading Session Timings (IST)
PRE_OPEN_START = time(9, 0, 0)
PRE_OPEN_END = time(9, 8, 0)
ORDER_MATCHING_END = time(9, 15, 0)
MARKET_OPEN = time(9, 15, 0)
MARKET_CLOSE = time(15, 30, 0)
POST_CLOSE_START = time(15, 40, 0)
POST_CLOSE_END = time(16, 0, 0)

# Official NSE / BSE Trading Holidays (2024 - 2027)
NSE_HOLIDAYS: Dict[date, str] = {
    # 2024
    date(2024, 1, 22): "Special Holiday (Ayodhya Pran Pratishtha)",
    date(2024, 1, 26): "Republic Day",
    date(2024, 3, 8): "Mahashivratri",
    date(2024, 3, 25): "Holi",
    date(2024, 3, 29): "Good Friday",
    date(2024, 4, 11): "Id-Ul-Fitr (Ramadan Eid)",
    date(2024, 4, 17): "Shri Ram Navami",
    date(2024, 5, 1): "Maharashtra Day",
    date(2024, 5, 20): "General Parliamentary Elections (Mumbai)",
    date(2024, 6, 17): "Bakri Id / Id-Ul-Adha",
    date(2024, 7, 17): "Muharram",
    date(2024, 8, 15): "Independence Day",
    date(2024, 10, 2): "Mahatma Gandhi Jayanti",
    date(2024, 11, 1): "Diwali - Laxmi Pujan (Muhurat Trading in evening)",
    date(2024, 11, 15): "Gurunanak Jayanti",
    date(2024, 11, 20): "Maharashtra Assembly Elections",
    date(2024, 12, 25): "Christmas",
    # 2025
    date(2025, 2, 26): "Mahashivratri",
    date(2025, 3, 14): "Holi",
    date(2025, 3, 31): "Id-Ul-Fitr",
    date(2025, 4, 10): "Shri Mahavir Jayanti",
    date(2025, 4, 14): "Dr. Baba Saheb Ambedkar Jayanti",
    date(2025, 4, 18): "Good Friday",
    date(2025, 5, 1): "Maharashtra Day",
    date(2025, 6, 7): "Bakri Id",
    date(2025, 8, 15): "Independence Day",
    date(2025, 8, 27): "Ganesh Chaturthi",
    date(2025, 10, 2): "Mahatma Gandhi Jayanti",
    date(2025, 10, 21): "Diwali - Laxmi Pujan (Muhurat Trading)",
    date(2025, 10, 22): "Diwali - Balipratipada",
    date(2025, 11, 5): "Prakash Gurpurb Sri Guru Nanak Dev",
    date(2025, 12, 25): "Christmas",
    # 2026
    date(2026, 1, 26): "Republic Day",
    date(2026, 2, 16): "Mahashivratri",
    date(2026, 3, 4): "Holi",
    date(2026, 3, 20): "Id-Ul-Fitr",
    date(2026, 4, 3): "Good Friday",
    date(2026, 4, 14): "Dr Ambedkar Jayanti",
    date(2026, 5, 1): "Maharashtra Day",
    date(2026, 5, 28): "Bakri Id",
    date(2026, 6, 26): "Muharram",
    date(2026, 8, 15): "Independence Day",
    date(2026, 10, 2): "Mahatma Gandhi Jayanti",
    date(2026, 10, 20): "Dussehra",
    date(2026, 11, 9): "Diwali - Laxmi Pujan",
    date(2026, 11, 24): "Guru Nanak Jayanti",
    date(2026, 12, 25): "Christmas",
    # 2027
    date(2027, 1, 26): "Republic Day",
    date(2027, 3, 8): "Mahashivratri",
    date(2027, 3, 23): "Holi",
    date(2027, 3, 26): "Good Friday",
    date(2027, 4, 14): "Dr Ambedkar Jayanti",
    date(2027, 5, 1): "Maharashtra Day",
    date(2027, 8, 15): "Independence Day",
    date(2027, 10, 2): "Mahatma Gandhi Jayanti",
    date(2027, 12, 25): "Christmas",
}

# Special Muhurat Trading Days (1-hour evening session)
SPECIAL_SESSIONS: Dict[date, Tuple[time, time, str]] = {
    date(2024, 11, 1): (time(18, 0), time(19, 0), "Diwali Muhurat Trading 2024"),
    date(2025, 10, 21): (time(18, 15), time(19, 15), "Diwali Muhurat Trading 2025"),
    date(2026, 11, 9): (time(18, 15), time(19, 15), "Diwali Muhurat Trading 2026"),
}


class IndianMarketCalendar:
    """Exchange-aware calendar for Indian Equities and Derivatives (NSE/BSE)."""

    def __init__(self, tz: pytz.BaseTzInfo = IST_TIMEZONE):
        self.tz = tz

    def now_ist(self) -> datetime:
        """Returns the current datetime localized to Asia/Kolkata (IST)."""
        return datetime.now(self.tz)

    def is_holiday(self, target_date: date) -> Tuple[bool, Optional[str]]:
        """Checks if a given date is an official market holiday."""
        if target_date in NSE_HOLIDAYS:
            return True, NSE_HOLIDAYS[target_date]
        return False, None

    def is_weekend(self, target_date: date) -> bool:
        """Saturday (5) or Sunday (6)."""
        return target_date.weekday() >= 5

    def is_trading_day(self, target_date: date) -> bool:
        """Returns True if the date is a regular trading day or special trading session."""
        if target_date in SPECIAL_SESSIONS:
            return True
        if self.is_weekend(target_date):
            return False
        is_hol, _ = self.is_holiday(target_date)
        return not is_hol

    def get_session_status(self, dt: Optional[datetime] = None) -> Tuple[MarketSessionStatus, str]:
        """
        Determines exact market session state for the given datetime (or now if None).
        Returns (Status, Human-readable descriptive name).
        """
        if dt is None:
            dt = self.now_ist()
        elif dt.tzinfo is None:
            dt = self.tz.localize(dt)
        else:
            dt = dt.astimezone(self.tz)

        current_date = dt.date()
        current_time = dt.time()

        # Check for Special Muhurat Trading Session
        if current_date in SPECIAL_SESSIONS:
            s_start, s_end, s_name = SPECIAL_SESSIONS[current_date]
            if s_start <= current_time <= s_end:
                return MarketSessionStatus.SPECIAL_SESSION, s_name

        # Check Weekend
        if self.is_weekend(current_date):
            return MarketSessionStatus.WEEKEND, "Market Closed (Weekend)"

        # Check Holiday
        is_hol, hol_name = self.is_holiday(current_date)
        if is_hol:
            return MarketSessionStatus.HOLIDAY, f"Market Closed (Holiday: {hol_name})"

        # Check Trading Hours on a regular trading day
        if PRE_OPEN_START <= current_time < PRE_OPEN_END:
            return MarketSessionStatus.PRE_OPEN, "Pre-Open Session (Order Entry)"
        elif PRE_OPEN_END <= current_time < ORDER_MATCHING_END:
            return MarketSessionStatus.PRE_OPEN, "Pre-Open Session (Order Matching)"
        elif MARKET_OPEN <= current_time <= MARKET_CLOSE:
            return MarketSessionStatus.OPEN, "Regular Market Hours"
        elif POST_CLOSE_START <= current_time <= POST_CLOSE_END:
            return MarketSessionStatus.POST_CLOSE, "Post-Close Session"
        elif current_time < PRE_OPEN_START:
            return MarketSessionStatus.CLOSED, "Market Closed (Pre-Market Hours)"
        else:
            return MarketSessionStatus.CLOSED, "Market Closed (After Hours)"

    def get_next_market_open(self, dt: Optional[datetime] = None) -> datetime:
        """Returns the upcoming regular market open datetime (09:15 IST)."""
        if dt is None:
            dt = self.now_ist()
        elif dt.tzinfo is None:
            dt = self.tz.localize(dt)
        else:
            dt = dt.astimezone(self.tz)

        check_date = dt.date()
        # If today is a trading day and time is before 09:15:
        if self.is_trading_day(check_date) and dt.time() < MARKET_OPEN:
            return self.tz.localize(datetime.combine(check_date, MARKET_OPEN))

        # Otherwise look at next days
        check_date += timedelta(days=1)
        while not self.is_trading_day(check_date):
            check_date += timedelta(days=1)

        return self.tz.localize(datetime.combine(check_date, MARKET_OPEN))

    def get_next_market_close(self, dt: Optional[datetime] = None) -> datetime:
        """Returns the upcoming regular market close datetime (15:30 IST)."""
        if dt is None:
            dt = self.now_ist()
        elif dt.tzinfo is None:
            dt = self.tz.localize(dt)
        else:
            dt = dt.astimezone(self.tz)

        check_date = dt.date()
        if self.is_trading_day(check_date) and dt.time() < MARKET_CLOSE:
            return self.tz.localize(datetime.combine(check_date, MARKET_CLOSE))

        # Next open day close
        next_open = self.get_next_market_open(dt)
        return self.tz.localize(datetime.combine(next_open.date(), MARKET_CLOSE))

    def get_expiry_date(self, target_date: date, day_of_week: int = 3) -> date:
        """
        Calculates weekly or monthly expiry date for a given week/month.
        Default day_of_week is 3 (Thursday for NIFTY / Monthly Derivatives).
        If the calculated day falls on a holiday, it automatically rolls to the prior trading day.
        """
        # Find next occurrence of target day_of_week in the same week
        days_ahead = day_of_week - target_date.weekday()
        expiry_candidate = target_date + timedelta(days=days_ahead)

        # Roll back if holiday or weekend
        while not self.is_trading_day(expiry_candidate):
            expiry_candidate -= timedelta(days=1)

        return expiry_candidate

    def get_monthly_expiry(self, year: int, month: int) -> date:
        """
        Calculates the monthly F&O expiry (Last Thursday of the month, adjusted for holidays).
        """
        # Find last day of month
        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)
        last_day = next_month - timedelta(days=1)

        # Walk backwards to find the last Thursday (weekday == 3)
        offset = (last_day.weekday() - 3) % 7
        last_thursday = last_day - timedelta(days=offset)

        # Roll backwards if last Thursday is a holiday
        while not self.is_trading_day(last_thursday):
            last_thursday -= timedelta(days=1)

        return last_thursday
