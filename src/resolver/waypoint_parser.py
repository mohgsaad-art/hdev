# STATUS: NEW (Step 9, item 1 / M0.0, Bob to review). Fresh VDRI + .vacc parsers.
# PIPELINE STEP: input layer -> waypoint list (feeds the driver model, step G).
# Reference ONLY (not imported): src/deprecated/simulate_driver_alt.py parse_vdri_text / parse_vacc_text.
# PURITY (engine rule 7): both functions take the pasted TEXT as a string argument. No file reads,
#   no disk/network inside the parser - the caller is responsible for loading the text.
# FAIL LOUDLY (engine rule 6): raise ValueError when no valid rows are found.
# OUTPUT SHAPE: the Waypoint fields are named to match what driver_model.DriverModel reads directly -
#   it accesses .distance, .speed, .stop, .grade_pct on each waypoint, and .speed, .acc, .dec on each
#   vacc point. So the parser output drops straight into the driver model with no adapter.
# UNITS: distance in metres, speed in km/h (the driver model converts km/h -> m/s itself),
#   grade in %, stop in seconds. acc/dec in m/s^2. km/h is kept here because this is the input edge.

import csv
from dataclasses import dataclass
from io import StringIO
from typing import List


# ---------------------------------------------------------------------------
# Data structures (attribute names match what driver_model.py reads)
# ---------------------------------------------------------------------------

@dataclass
class Waypoint:
    # one VDRI row. driver_model reads .distance, .speed, .stop, .grade_pct
    distance: float    # distance along the route, m (VDRI <s>)
    speed: float       # target speed at this waypoint, km/h (VDRI <v>)
    grade_pct: float   # road gradient at this waypoint, % (VDRI <grad>)
    stop: float        # stop duration at this waypoint, s (VDRI <stop>)


@dataclass
class VaccPoint:
    # one accel/decel curve point. driver_model reads .speed, .acc, .dec
    speed: float   # speed the curve point is defined at, km/h
    acc: float     # max acceleration at this speed, m/s^2
    dec: float     # max deceleration at this speed, m/s^2 (negative)


# ---------------------------------------------------------------------------
# Parsers for pasted string data
# ---------------------------------------------------------------------------

def parse_vdri_text(text):
    # parse a VDRI mission-cycle text (pasted as a string) into a list of Waypoint.
    # column order is distance, speed, grade, stop - the VECTO <s>,<v>,<grad>,<stop> header.
    # header rows (<...>) and comment rows (#) are skipped, as are rows that do not parse.
    if text is None:
        raise ValueError("parse_vdri_text: text is None")

    waypoints = []
    text = text.replace("\ufeff", "")  # strip a leading BOM if the paste carried one
    reader = csv.reader(StringIO(text.strip()))

    for row in reader:
        row = [c.strip() for c in row]

        # skip blank, header (<s>,<v>,...) and comment (#) rows
        if not row or row[0] == "" or row[0].startswith("<") or row[0].startswith("#"):
            continue

        try:
            distance = float(row[0])
            speed = float(row[1])
            grade_pct = float(row[2])
            stop = float(row[3])
        except (ValueError, IndexError):
            continue

        waypoints.append(Waypoint(distance, speed, grade_pct, stop))

    if not waypoints:
        raise ValueError("parse_vdri_text: no valid VDRI waypoints found in pasted text")

    return waypoints


def parse_vacc_text(text):
    # parse a .vacc accel/decel curve text (pasted as a string) into a list of VaccPoint,
    # sorted ascending by speed (the driver-model lookup assumes a sorted curve).
    # column order is speed, acc, dec. header/comment/unparseable rows are skipped.
    if text is None:
        raise ValueError("parse_vacc_text: text is None")

    points = []
    text = text.replace("\ufeff", "")
    reader = csv.reader(StringIO(text.strip()))

    for row in reader:
        row = [c.strip() for c in row]

        if not row or row[0] == "" or row[0].startswith("<") or row[0].startswith("#"):
            continue

        try:
            speed = float(row[0])
            acc = float(row[1])
            dec = float(row[2])
        except (ValueError, IndexError):
            continue

        points.append(VaccPoint(speed, acc, dec))

    if not points:
        raise ValueError("parse_vacc_text: no valid VACC points found in pasted text")

    return sorted(points, key=lambda p: p.speed)
