# STATUS: NEW (Step 9 items 9-14). Hand-checked unit tests for the calendar/sizing/charging/AI-adapter
#   block. conftest.py puts repo root on sys.path so imports resolve as src.resolver.* / src.charging.*.
# Every expected number is a hand-checked case with the arithmetic written out in the test. None of these
# modules may import gym at load (the thesis env ev_charging_env.py imports gym; the pure path must not).

import datetime as dt

import pytest


# ---------------------------------------------------------------------------
# ITEM 9 - calendar expand (pattern -> dated operating days, Danish holidays)
# ---------------------------------------------------------------------------

from src.resolver.calendar import (
    build_calendar,
    standard_danish_holidays,
    easter_sunday,
)


def _two_weeks_weather():
    # Dec 14 2026 (Mon) .. Dec 27 2026 (Sun): 14 consecutive dates with trivial weather supplied.
    return {dt.date(2026, 12, d): {"T": 2.0, "wind": 5.0} for d in range(14, 28)}


def test_build_calendar_expands_two_week_weekday_pattern():
    # 2026-12-14 (Mon) .. 2026-12-27 (Sun) is exactly two calendar weeks = 14 dates.
    # weekdays pattern -> 10 Mon-Fri dates, but 2026-12-25 (Fri, Christmas Day) is a holiday.
    # So operating days = 10 - 1 = 9. Hand-counted:
    #   wk1 Mon14 Tue15 Wed16 Thu17 Fri18          -> 5
    #   wk2 Mon21 Tue22 Wed23 Thu24 (Fri25 holiday) -> 4
    #   total 9.
    holidays = {dt.date(2026, 12, 25), dt.date(2026, 12, 26)}
    cal = build_calendar(
        dt.date(2026, 12, 14), dt.date(2026, 12, 27),
        "weekdays", _two_weeks_weather(), holidays,
    )
    assert len(cal["rows"]) == 14
    assert cal["operating_days"] == 9

    # the known Danish holiday 2026-12-25 is non-operating
    row_dec25 = next(r for r in cal["rows"] if r["date"] == dt.date(2026, 12, 25))
    assert row_dec25["operating"] is False
    assert row_dec25["day_type"] is None

    # a normal operating weekday carries the day-type and the supplied weather
    row_dec14 = next(r for r in cal["rows"] if r["date"] == dt.date(2026, 12, 14))
    assert row_dec14["operating"] is True
    assert row_dec14["day_type"] == "default"
    assert row_dec14["T"] == 2.0 and row_dec14["wind"] == 5.0

    # weekend dates are non-operating under the weekdays pattern
    row_dec19 = next(r for r in cal["rows"] if r["date"] == dt.date(2026, 12, 19))  # Saturday
    assert row_dec19["operating"] is False

    # the holiday-set assumption is surfaced, not applied silently
    assert any("HOLIDAY SET ASSUMPTION" in a for a in cal["assumptions"])


def test_easter_based_holidays_and_great_prayer_day_rule():
    # Easter Sunday 2026 is 2026-04-05 (hand/reference checked).
    assert easter_sunday(2026) == dt.date(2026, 4, 5)
    # Great Prayer Day = 4th Friday after Easter = Easter + 26 days.
    gpd_2023 = easter_sunday(2023) + dt.timedelta(days=26)
    gpd_2026 = easter_sunday(2026) + dt.timedelta(days=26)
    # statutory in 2023, abolished from 2024 -> present in 2023 set, absent in 2026 set (default rule).
    assert gpd_2023 in standard_danish_holidays(2023)
    assert gpd_2026 not in standard_danish_holidays(2026)
    # forcing it on brings it back for 2026
    assert gpd_2026 in standard_danish_holidays(2026, include_great_prayer_day=True)
    # contested days OFF by default, ON when switched
    assert dt.date(2026, 6, 5) not in standard_danish_holidays(2026)
    assert dt.date(2026, 6, 5) in standard_danish_holidays(2026, include_constitution_day=True)


def test_build_calendar_raises_on_operating_date_without_weather():
    # an operating date with no weather entry must raise (weather is never invented).
    with pytest.raises(ValueError):
        build_calendar(
            dt.date(2026, 1, 5), dt.date(2026, 1, 5),  # a Monday
            "weekdays", {}, set(),
        )


def test_build_calendar_rejects_bad_date_order_and_unknown_pattern():
    with pytest.raises(ValueError):
        build_calendar(dt.date(2026, 1, 2), dt.date(2026, 1, 1), "weekdays", {}, set())
    with pytest.raises(ValueError):
        build_calendar(
            dt.date(2026, 1, 5), dt.date(2026, 1, 5),
            "every-third-tuesday", _two_weeks_weather(), set(),
        )
