# STATUS: NEW (Step 9, item 9 / M2.4, Bob to review). Calendar expand: pattern -> dated operating days.
# PIPELINE ROLE: the "pattern input vs full-year" flow (docs/design/year-and-day-simulation-problem.md
#   section 2 "Calendar and grouping"): one row per date carrying operating yes/no, the day-type, and the
#   day's weather (T, wind). Consumption does NOT read the calendar; it is used for weather lookups, the
#   charging sequence and annual totals.
# PURITY (engine rule 7): every parameter is an argument. Weather comes IN as weather_by_date (no DMI
#   fetch inside). The exact Danish-holiday SET also comes in as an argument - we never silently
#   hard-code a contested set (see the holiday notes below).
# FAIL LOUDLY (engine rule 6): bad date order, unknown operating-pattern keyword, or a date with no
#   weather entry raise. No invented weather: a missing weather entry is an error, not a guessed value.
#
# ---------------------------------------------------------------------------
# DANISH PUBLIC HOLIDAYS - why the SET is an ARGUMENT, not hard-coded
# ---------------------------------------------------------------------------
# The movable feasts (Maundy Thursday, Good Friday, Easter Monday, Great Prayer Day, Ascension,
# Whit Monday) are all offsets from Easter Sunday, which we CAN compute (Anonymous Gregorian / Meeus
# algorithm, no source needed - it is arithmetic). easter_sunday() and standard_danish_holidays()
# below do that. BUT which days actually count as non-operating is a contested policy choice:
#   - Great Prayer Day (Store Bededag, 4th Friday after Easter) was ABOLISHED as a public holiday
#     from 2024 (Danish law, Dec 2023). So it is a holiday <= 2023 and NOT from 2024 on.
#   - Constitution Day (Grundlovsdag, Jun 5) and Christmas Eve (Dec 24) are NOT statutory public
#     holidays; many but not all workplaces close (often as half-days). Treating them as
#     non-operating is an ASSUMPTION about the specific fleet, not a fact.
# Because of that, build_calendar takes the FINAL danish_holidays set from the caller and FLAGS it as an
# assumption. standard_danish_holidays() is a HELPER the caller can start from (with explicit
# include_great_prayer_day / include_constitution_day / include_christmas_eve switches), but the caller
# owns the decision and the flag. We never bake a contested set into the engine.

import datetime as _dt


# ---------------------------------------------------------------------------
# Easter + the standard Danish holiday helper (arithmetic, caller still decides the final set)
# ---------------------------------------------------------------------------

def easter_sunday(year):
    # Easter Sunday for a Gregorian year via the Anonymous Gregorian algorithm (Meeus/Jones/Butcher).
    # Pure integer arithmetic - no source needed, this is the definition of the date.
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return _dt.date(year, month, day)


def standard_danish_holidays(
    year,
    include_great_prayer_day=None,
    include_constitution_day=False,
    include_christmas_eve=False,
):
    # Build a HELPER set of Danish public-holiday dates for one year. The caller still owns the final
    # decision and must flag it; this just saves the caller the Easter arithmetic.
    #
    # Fixed-date statutory holidays: New Year (Jan 1), Christmas Day + Boxing Day (Dec 25-26).
    # Easter-based statutory holidays: Maundy Thursday (-3), Good Friday (-2), Easter Monday (+1),
    #   Ascension (+39), Whit Monday (+50).
    # Great Prayer Day (Store Bededag, +26, the 4th Friday after Easter): statutory UP TO 2023,
    #   ABOLISHED from 2024. If include_great_prayer_day is None we apply that legal rule by year;
    #   pass True/False to force it.
    # Constitution Day (Jun 5) and Christmas Eve (Dec 24): OFF by default (not statutory); switch on
    #   only as an explicit, flagged fleet assumption.
    easter = easter_sunday(year)
    days = set()

    # fixed statutory
    days.add(_dt.date(year, 1, 1))     # Nytarsdag / New Year
    days.add(_dt.date(year, 12, 25))   # Juledag / Christmas Day
    days.add(_dt.date(year, 12, 26))   # 2. juledag / Boxing Day

    # Easter-based statutory
    days.add(easter - _dt.timedelta(days=3))   # Skaertorsdag / Maundy Thursday
    days.add(easter - _dt.timedelta(days=2))   # Langfredag / Good Friday
    days.add(easter + _dt.timedelta(days=1))   # 2. paaskedag / Easter Monday
    days.add(easter + _dt.timedelta(days=39))  # Kristi himmelfartsdag / Ascension
    days.add(easter + _dt.timedelta(days=50))  # 2. pinsedag / Whit Monday

    # Great Prayer Day: statutory <= 2023, abolished from 2024 (apply the legal rule unless forced)
    if include_great_prayer_day is None:
        gpd = year <= 2023
    else:
        gpd = bool(include_great_prayer_day)
    if gpd:
        days.add(easter + _dt.timedelta(days=26))  # Store Bededag / Great Prayer Day

    # contested, OFF by default
    if include_constitution_day:
        days.add(_dt.date(year, 6, 5))   # Grundlovsdag / Constitution Day
    if include_christmas_eve:
        days.add(_dt.date(year, 12, 24))  # Juleaftensdag / Christmas Eve

    return days


# ---------------------------------------------------------------------------
# Operating-pattern matcher
# ---------------------------------------------------------------------------

# supported pattern keywords -> the set of Python weekday() numbers that OPERATE
# (Monday=0 .. Sunday=6). Anything else must be a per-date callable (see _pattern_operates).
_PATTERN_WEEKDAYS = {
    "weekdays": {0, 1, 2, 3, 4},            # Mon-Fri
    "mon-fri": {0, 1, 2, 3, 4},
    "mon-sat": {0, 1, 2, 3, 4, 5},
    "everyday": {0, 1, 2, 3, 4, 5, 6},
    "all": {0, 1, 2, 3, 4, 5, 6},
    "weekends": {5, 6},
}


def _pattern_operates(operating_pattern, date):
    # does operating_pattern say this date is a candidate operating day (before holidays)?
    # operating_pattern may be:
    #   - a string keyword from _PATTERN_WEEKDAYS,
    #   - a set/list of weekday numbers (0=Mon..6=Sun),
    #   - a callable date -> bool (for odd patterns the UI builds explicitly).
    if callable(operating_pattern):
        return bool(operating_pattern(date))
    if isinstance(operating_pattern, (set, frozenset, list, tuple)):
        return date.weekday() in set(operating_pattern)
    if isinstance(operating_pattern, str):
        key = operating_pattern.strip().lower()
        if key not in _PATTERN_WEEKDAYS:
            raise ValueError(
                "build_calendar: unknown operating_pattern %r (known: %s, or pass a set of "
                "weekday numbers / a callable)" % (operating_pattern, sorted(_PATTERN_WEEKDAYS))
            )
        return date.weekday() in _PATTERN_WEEKDAYS[key]
    raise ValueError(
        "build_calendar: operating_pattern must be a keyword string, a set of weekday numbers, "
        "or a callable, got %r" % (operating_pattern,)
    )


# ---------------------------------------------------------------------------
# The calendar expand
# ---------------------------------------------------------------------------

def build_calendar(
    start_date,
    end_date,
    operating_pattern,
    weather_by_date,
    danish_holidays,
    day_type="default",
):
    # Expand an operating PATTERN into one row per date across [start_date, end_date] inclusive.
    #
    # Arguments (all passed in - pure function):
    #   start_date, end_date : datetime.date (or ISO 'YYYY-MM-DD' strings). end_date >= start_date.
    #   operating_pattern    : weekday keyword / set / callable (see _pattern_operates). Marks which
    #                          weekdays are candidate operating days before holidays are removed.
    #   weather_by_date      : {date -> {'T': temp_C, 'wind': wind_mps}} supplying the day's weather.
    #                          Weather is an INPUT (engine rule 7); a missing OPERATING date raises
    #                          (no invented weather). Non-operating dates may be absent -> T/wind None.
    #   danish_holidays      : the FINAL set of holiday dates (see module notes). A date in this set is
    #                          NON-operating even if the pattern would run it. The caller built and
    #                          FLAGGED this set (standard_danish_holidays() is the suggested starting
    #                          point); build_calendar does not decide it.
    #   day_type             : label stamped on operating rows (route / day-type grouping key).
    #
    # Returns a dict:
    #   {'rows': [ {date, operating(bool), day_type, T, wind}, ... one per date ... ],
    #    'operating_days': int,
    #    'assumptions': [ ...flag strings... ]}
    # The holiday set is reported in 'assumptions' as an explicit assumption, so nothing contested is
    # applied silently.

    start = _coerce_date(start_date, "start_date")
    end = _coerce_date(end_date, "end_date")
    if end < start:
        raise ValueError(
            "build_calendar: end_date %s is before start_date %s" % (end.isoformat(), start.isoformat())
        )
    if weather_by_date is None:
        raise ValueError("build_calendar: weather_by_date is required (weather comes in as an argument)")

    # normalise the holiday set to datetime.date (accept ISO strings too)
    holidays = set()
    if danish_holidays:
        for h in danish_holidays:
            holidays.add(_coerce_date(h, "danish_holidays entry"))

    rows = []
    operating_days = 0
    one_day = _dt.timedelta(days=1)
    date = start
    while date <= end:
        is_candidate = _pattern_operates(operating_pattern, date)
        is_holiday = date in holidays
        operating = bool(is_candidate and not is_holiday)

        T = None
        wind = None
        if date in weather_by_date and weather_by_date[date] is not None:
            w = weather_by_date[date]
            T = w.get("T")
            wind = w.get("wind")
        elif operating:
            # an operating day with no weather is a hard error - we never guess weather.
            raise ValueError(
                "build_calendar: operating date %s has no weather entry in weather_by_date "
                "(weather must be supplied, never invented)" % date.isoformat()
            )

        rows.append({
            "date": date,
            "operating": operating,
            "day_type": day_type if operating else None,
            "T": T,
            "wind": wind,
        })
        if operating:
            operating_days += 1
        date += one_day

    assumptions = [
        "HOLIDAY SET ASSUMPTION: %d Danish holiday date(s) supplied by the caller were treated as "
        "non-operating. The exact set (incl. whether Great Prayer Day/Store Bededag, Constitution Day "
        "and Christmas Eve count) is a flagged policy/fleet assumption, not a fact baked into the engine."
        % (len(holidays),),
    ]

    return {"rows": rows, "operating_days": operating_days, "assumptions": assumptions}


def _coerce_date(value, label):
    # accept a datetime.date or an ISO 'YYYY-MM-DD' string; fail loudly otherwise.
    if isinstance(value, _dt.date) and not isinstance(value, _dt.datetime):
        return value
    if isinstance(value, _dt.datetime):
        return value.date()
    if isinstance(value, str):
        try:
            return _dt.date.fromisoformat(value.strip())
        except ValueError:
            raise ValueError("build_calendar: %s %r is not an ISO date (YYYY-MM-DD)" % (label, value))
    raise ValueError("build_calendar: %s must be a date or ISO string, got %r" % (label, value))
