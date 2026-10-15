# STATUS: NEW (Step 9, item 10 / M2.6, Bob to review). The session hand-over object between the
#   consumption step (energy per operating day) and the charging simulation (per plug-in session).
#
# ---------------------------------------------------------------------------
# tasks.md 🔒 vs master-prompt "Decided" - reconciliation (REQUIRED note)
# ---------------------------------------------------------------------------
# tasks.md still marks M2.6 as 🔒 ("confirm fields"). The master prompt §6 item 10 says
# "Decided - write" and §3 gives the hand-over its exact shape: EXACTLY four fields
#   {arrival, departure, energy_need_kWh, arrival_SOC}.
# Per the engine rules and the orchestrator brief, the MASTER PROMPT wins when it says "decided", so we
# implement exactly those four fields. We deliberately do NOT add any unconfirmed field - in particular
# NOT departure_time, which is the SEPARATE still-locked item M2.7 (a per-date departure clock time that
# option-C hourly weather would need). Adding it here would be deciding a 🔒 item, which the rules forbid.
# If Bob later confirms M2.6 with a different shape, this is the single place to change it.
#
# PIPELINE ROLE (docs/design/year-and-day-simulation-problem.md section 3 "Charging over days and
#   weeks"): charging is simulated per plug-in SESSION (arrival -> next departure), not per calendar day.
#   SOC carries over from one session to the next. This object is the hand-over the charging run walks.
# PURITY (engine rule 7): the builder takes already-computed structured arguments; no I/O, no reading
#   consumption or the calendar from disk - the caller passes the per-day energy and arrival SOC in.
# FAIL LOUDLY (engine rule 6): departure not after arrival, negative energy, SOC outside [0,1] -> raise.

import datetime as _dt
from dataclasses import dataclass
from typing import List


# ---------------------------------------------------------------------------
# The hand-over object - EXACTLY the four §3 fields, nothing else
# ---------------------------------------------------------------------------

@dataclass
class ChargingSession:
    # one depot plug-in session (arrival -> next departure). EXACTLY the four decided fields:
    arrival: _dt.datetime        # when the truck plugs in (absolute clock time)
    departure: _dt.datetime      # when it must leave for the next operating day (absolute clock time)
    energy_need_kWh: float       # energy that must be returned to the pack before departure, kWh
    arrival_SOC: float           # state of charge at arrival, fraction in [0, 1]
    # NOTE: no departure_time field here on purpose (that is the separate 🔒 M2.7); see module header.


def build_sessions(day_energy_rows, start_soc, usable_pack_kwh):
    # Build the ordered list of ChargingSession objects from the consumption output + calendar sequence.
    #
    # Arguments (all passed in - pure function):
    #   day_energy_rows : ordered list of operating-day dicts, each with
    #       {'arrival': datetime, 'departure': datetime, 'energy_used_kWh': float}
    #     where energy_used_kWh is the drive energy consumed on the day that preceded this plug-in
    #     (the energy that now has to be charged back). The list must already be in chronological order
    #     (the calendar built it); this builder does not sort or fetch anything.
    #   start_soc       : SOC fraction in [0,1] at the FIRST arrival (carried in, never invented).
    #   usable_pack_kwh : usable battery energy (kWh) used to turn an energy need into an SOC delta and
    #     to carry SOC date-to-date. Required argument (no default - battery size is a scenario input).
    #
    # SOC carry-over model (matches the design doc "SOC carries over across sessions"):
    #   arrival_SOC[0]   = start_soc
    #   energy_need_kWh  = the day's drive energy (what must be put back before departure)
    #   next arrival_SOC = min(1.0, this arrival_SOC + energy_need_kWh / usable_pack_kwh)
    #     i.e. we ASSUME the session fully meets the need (the charging run itself decides whether the
    #     site cap / dwell actually allows that; this builder only lays out the hand-over, and the
    #     charging sim overwrites the carried SOC with the real ending SOC). This neutral assumption is
    #     flagged in 'assumptions'.
    #
    # Returns {'sessions': [ChargingSession, ...], 'assumptions': [...]}.
    if usable_pack_kwh is None or usable_pack_kwh <= 0:
        raise ValueError("build_sessions: usable_pack_kwh must be > 0, got %r" % (usable_pack_kwh,))
    if start_soc is None or not (0.0 <= start_soc <= 1.0):
        raise ValueError("build_sessions: start_soc must be in [0,1], got %r" % (start_soc,))
    if day_energy_rows is None:
        raise ValueError("build_sessions: day_energy_rows is required")

    sessions: List[ChargingSession] = []
    soc = float(start_soc)

    for idx, row in enumerate(day_energy_rows):
        arrival = row.get("arrival")
        departure = row.get("departure")
        energy = row.get("energy_used_kWh")

        if arrival is None or departure is None:
            raise ValueError("build_sessions: row %d missing arrival/departure" % idx)
        if not isinstance(arrival, _dt.datetime) or not isinstance(departure, _dt.datetime):
            raise ValueError("build_sessions: row %d arrival/departure must be datetime" % idx)
        if departure <= arrival:
            raise ValueError(
                "build_sessions: row %d departure %s is not after arrival %s"
                % (idx, departure.isoformat(), arrival.isoformat())
            )
        if energy is None or energy < 0:
            raise ValueError("build_sessions: row %d energy_used_kWh must be >= 0, got %r" % (idx, energy))

        sessions.append(ChargingSession(
            arrival=arrival,
            departure=departure,
            energy_need_kWh=float(energy),
            arrival_SOC=soc,
        ))

        # carry SOC to the next session (neutral: assume the need is met; charging sim corrects it later)
        soc = min(1.0, soc + float(energy) / float(usable_pack_kwh))

    assumptions = [
        "SOC CARRY-OVER ASSUMPTION: build_sessions assumes each session fully meets its energy need, "
        "so the next arrival_SOC = min(1, arrival_SOC + energy_need_kWh / usable_pack_kwh). The charging "
        "simulation overwrites this with the REAL ending SOC when the site cap or dwell limits delivery.",
        "FIELD SET: hand-over carries EXACTLY {arrival, departure, energy_need_kWh, arrival_SOC} per the "
        "master prompt 'decided' shape; tasks.md still marks M2.6 as locked ('confirm fields'). "
        "departure_time (M2.7) is intentionally NOT included.",
    ]
    return {"sessions": sessions, "assumptions": assumptions}
