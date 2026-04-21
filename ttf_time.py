"""TTF options — Time to Maturity utilities.

Provides T (time to expiry in years) from any combination of:
  - two date / datetime objects
  - expiry date string ("2026-03-31", "31Mar2026", "Mar26", "TTFH26", …)
  - delivery month + year integers
  - tenor string ("3M", "6M", "1Y", "2Y")

Day-count conventions supported:
  Act/365 (Fixed)  — TTF market standard, used everywhere in this project
  Act/360          — money-market reference
  Act/Act (ISDA)   — government bond standard
  Bus/252          — Brazilian / equity vol convention

The module is self-contained (stdlib + optional numpy) and may be imported
by both black76_ttf.py and ttf_market_data.py.
"""

from __future__ import annotations

import math
import re
from datetime import date, datetime, timedelta
from typing import Union

DateLike = Union[date, datetime, str]

# ---------------------------------------------------------------------------
# Holiday calendar (TARGET / ECB — relevant for EUR gas markets)
# ---------------------------------------------------------------------------

def _target_holidays(year: int) -> frozenset[date]:
    """Fixed and Easter-based TARGET2 holidays for *year*."""
    # Easter Sunday via Gaussian algorithm
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month, day = divmod(114 + h + l - 7 * m, 31)
    easter = date(year, month, day + 1)

    good_friday    = easter - timedelta(days=2)
    easter_monday  = easter + timedelta(days=1)

    return frozenset([
        date(year, 1, 1),    # New Year
        good_friday,
        easter_monday,
        date(year, 5, 1),    # Labour Day
        date(year, 12, 25),  # Christmas
        date(year, 12, 26),  # Boxing Day
    ])


def is_business_day(d: date, holidays: frozenset[date] | None = None) -> bool:
    """Return True if *d* is a Mon–Fri non-holiday."""
    if d.weekday() >= 5:          # Saturday=5, Sunday=6
        return False
    if holidays is None:
        holidays = _target_holidays(d.year)
    return d not in holidays


def next_business_day(d: date) -> date:
    """Return *d* if it is a business day, otherwise advance to the next one."""
    while not is_business_day(d):
        d += timedelta(days=1)
    return d


def prev_business_day(d: date) -> date:
    """Return *d* if it is a business day, otherwise step back to the previous one."""
    while not is_business_day(d):
        d -= timedelta(days=1)
    return d


def business_days_between(start: date, end: date) -> int:
    """Count TARGET2 business days in (start, end] — exclusive start, inclusive end."""
    if end <= start:
        return 0
    count = 0
    current = start + timedelta(days=1)
    while current <= end:
        if is_business_day(current):
            count += 1
        current += timedelta(days=1)
    return count


# ---------------------------------------------------------------------------
# Day-count fractions
# ---------------------------------------------------------------------------

class DayCount:
    """Namespace for day-count fraction conventions."""

    @staticmethod
    def act365(start: date, end: date) -> float:
        """Act/365 Fixed — TTF market standard."""
        return max((end - start).days / 365.0, 0.0)

    @staticmethod
    def act360(start: date, end: date) -> float:
        """Act/360 — money-market convention."""
        return max((end - start).days / 360.0, 0.0)

    @staticmethod
    def actact(start: date, end: date) -> float:
        """Act/Act ISDA — each calendar year weighted by its own length."""
        if end <= start:
            return 0.0
        total = 0.0
        y = start.year
        while y <= end.year:
            year_start = date(y, 1, 1)
            year_end   = date(y + 1, 1, 1)
            days_in_year = (year_end - year_start).days        # 365 or 366
            seg_start = max(start, year_start)
            seg_end   = min(end, year_end)
            if seg_end > seg_start:
                total += (seg_end - seg_start).days / days_in_year
            y += 1
        return total

    @staticmethod
    def bus252(start: date, end: date) -> float:
        """Bus/252 — business-day convention (used in equity/EM vol)."""
        return max(business_days_between(start, end) / 252.0, 0.0)


# ---------------------------------------------------------------------------
# Date parsing
# ---------------------------------------------------------------------------

_MONTH_ABBR = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    "f": 1, "g": 2, "h": 3, "j": 4, "k": 5, "m": 6,
    "n": 7, "q": 8, "u": 9, "v": 10, "x": 11, "z": 12,
}

_TENOR_RE = re.compile(r"^(\d+)(D|W|M|Y)$", re.IGNORECASE)
_ICE_CODE  = re.compile(r"^TTF([FGHJKMNQUVXZ])(\d{2})$", re.IGNORECASE)


def parse_date(value: DateLike, reference: date | None = None) -> date:
    """Convert *value* to a :class:`date`.

    Accepted formats
    ----------------
    date / datetime     returned as-is (date part only)
    "YYYY-MM-DD"        ISO 8601
    "DD-Mon-YYYY"       e.g. "31-Mar-2026"
    "DDMonYYYY"         e.g. "31Mar2026"
    "MonYY"             e.g. "Mar26"  → last business day of that month
    "TTFX26"            ICE contract code → expiry date
    "3M" / "6M" / "1Y"  tenor relative to *reference* (today if None)
    """
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    s = value.strip()
    ref = reference or date.today()

    # Tenor string: 3M, 6M, 1Y, 2Y, 30D, 2W …
    m = _TENOR_RE.match(s)
    if m:
        n, unit = int(m.group(1)), m.group(2).upper()
        if unit == "D":
            return ref + timedelta(days=n)
        if unit == "W":
            return ref + timedelta(weeks=n)
        if unit == "M":
            # advance by n months
            month = ref.month + n
            year  = ref.year + (month - 1) // 12
            month = (month - 1) % 12 + 1
            day   = min(ref.day, _days_in_month(year, month))
            return date(year, month, day)
        if unit == "Y":
            try:
                return date(ref.year + n, ref.month, ref.day)
            except ValueError:
                return date(ref.year + n, ref.month, 28)

    # ICE TTF contract code: TTFH26
    m = _ICE_CODE.match(s)
    if m:
        month_code = m.group(1).upper()
        yr2 = int(m.group(2))
        year = 2000 + yr2
        month = _MONTH_ABBR[month_code.lower()]
        # expiry = last business day of month before delivery
        delivery_first = date(year, month, 1)
        prev_month_last = delivery_first - timedelta(days=1)
        return prev_business_day(prev_month_last)

    # ISO 8601: YYYY-MM-DD
    try:
        return date.fromisoformat(s)
    except ValueError:
        pass

    # DD-Mon-YYYY or DDMonYYYY
    m2 = re.match(r"^(\d{1,2})[-/\s]?([A-Za-z]{3})[-/\s]?(\d{4})$", s)
    if m2:
        d, mo, y = int(m2.group(1)), m2.group(2).lower(), int(m2.group(3))
        return date(y, _MONTH_ABBR[mo[:3]], d)

    # MonYY: Mar26
    m3 = re.match(r"^([A-Za-z]{3})(\d{2})$", s)
    if m3:
        mo, yr2 = m3.group(1).lower(), int(m3.group(2))
        year  = 2000 + yr2
        month = _MONTH_ABBR[mo]
        # treat as last business day of that month
        return prev_business_day(
            date(year, month, 1) - timedelta(days=1)
            if month == 12
            else date(year, month + 1, 1) - timedelta(days=1)
        )

    raise ValueError(f"Cannot parse date: {value!r}")


def _days_in_month(year: int, month: int) -> int:
    if month == 12:
        return 31
    return (date(year, month + 1, 1) - date(year, month, 1)).days


# ---------------------------------------------------------------------------
# Main public API
# ---------------------------------------------------------------------------

def time_to_maturity(
    expiry: DateLike,
    reference: DateLike | None = None,
    convention: str = "act365",
) -> float:
    """Compute T (time to maturity in years) from *reference* to *expiry*.

    Parameters
    ----------
    expiry     : expiry date or any format accepted by :func:`parse_date`
                 ("2026-03-31", "TTFH26", "3M", "Mar26", …)
    reference  : valuation date (default: today)
    convention : day-count rule — one of:
                 "act365"  Act/365 Fixed  ← TTF market default
                 "act360"  Act/360
                 "actact"  Act/Act ISDA
                 "bus252"  Business/252

    Returns
    -------
    float  T ≥ 0 in years; returns 0 if expiry ≤ reference.

    Examples
    --------
    >>> time_to_maturity("2026-09-30")           # ACT/365 from today
    >>> time_to_maturity("TTFH26")               # March-26 TTF contract
    >>> time_to_maturity("3M")                   # 3-month tenor
    >>> time_to_maturity("2026-06-30", "2026-03-31")
    """
    ref = parse_date(reference) if reference is not None else date.today()
    exp = parse_date(expiry, reference=ref)

    fn = {
        "act365": DayCount.act365,
        "act360": DayCount.act360,
        "actact": DayCount.actact,
        "bus252": DayCount.bus252,
    }.get(convention.lower().replace("/", "").replace(" ", ""))

    if fn is None:
        raise ValueError(
            f"Unknown day-count convention '{convention}'. "
            "Use 'act365', 'act360', 'actact', or 'bus252'."
        )
    return fn(ref, exp)


def time_to_maturity_multi(
    expiries: list[DateLike],
    reference: DateLike | None = None,
    convention: str = "act365",
) -> list[float]:
    """Vectorised version of :func:`time_to_maturity` for a list of expiries."""
    ref = parse_date(reference) if reference is not None else date.today()
    return [time_to_maturity(e, ref, convention) for e in expiries]


def expiry_from_delivery(
    delivery_year: int,
    delivery_month: int,
) -> date:
    """TTF option expiry: last business day of the month before delivery.

    Follows ICE/EEX convention — the option stops trading before the
    futures delivery period starts.
    """
    delivery_first = date(delivery_year, delivery_month, 1)
    last_of_prev   = delivery_first - timedelta(days=1)
    return prev_business_day(last_of_prev)


def t_from_delivery(
    delivery_year: int,
    delivery_month: int,
    reference: DateLike | None = None,
    convention: str = "act365",
) -> float:
    """T (years) from *reference* to the TTF option expiry for a given delivery month."""
    exp = expiry_from_delivery(delivery_year, delivery_month)
    return time_to_maturity(exp, reference, convention)


# ---------------------------------------------------------------------------
# Convenience: breakdown of T into days / business days
# ---------------------------------------------------------------------------

def maturity_breakdown(
    expiry: DateLike,
    reference: DateLike | None = None,
) -> dict:
    """Return a dict with calendar days, business days, and T under all conventions."""
    ref = parse_date(reference) if reference is not None else date.today()
    exp = parse_date(expiry, reference=ref)
    cal_days = max((exp - ref).days, 0)
    bus_days = business_days_between(ref, exp)
    return {
        "reference":   ref.isoformat(),
        "expiry":      exp.isoformat(),
        "cal_days":    cal_days,
        "bus_days":    bus_days,
        "T_act365":    DayCount.act365(ref, exp),
        "T_act360":    DayCount.act360(ref, exp),
        "T_actact":    DayCount.actact(ref, exp),
        "T_bus252":    DayCount.bus252(ref, exp),
    }


# ---------------------------------------------------------------------------
# Quick demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from datetime import date as _d
    ref = _d(2026, 4, 21)

    examples = [
        ("2026-09-30",  "ISO date"),
        ("TTFH26",      "ICE contract code (March 2026)"),
        ("TTFU26",      "ICE contract code (Sept 2026)"),
        ("3M",          "3-month tenor"),
        ("6M",          "6-month tenor"),
        ("1Y",          "1-year tenor"),
        ("Mar26",       "MonYY short format"),
        ("30Sep2026",   "DDMonYYYY format"),
    ]

    print(f"{'Input':<22} {'Description':<34} {'T_act365':>9} {'Cal days':>9} {'Bus days':>9}")
    print("-" * 86)
    for val, desc in examples:
        try:
            bd = maturity_breakdown(val, ref)
            print(
                f"{val:<22} {desc:<34} "
                f"{bd['T_act365']:>9.4f} {bd['cal_days']:>9} {bd['bus_days']:>9}"
            )
        except Exception as e:
            print(f"{val:<22} {desc:<34}  ERROR: {e}")

    print()
    print("Delivery-based T:")
    for yr, mo, name in [(2026, 6, "Jun-26"), (2026, 9, "Sep-26"), (2027, 3, "Mar-27")]:
        t = t_from_delivery(yr, mo, ref)
        exp = expiry_from_delivery(yr, mo)
        print(f"  {name}  expiry={exp}  T={t:.4f}y")
