#!/usr/bin/env python3
"""Validate the EV Scope UX input register against the authoritative map.

Inventory policy
----------------
The checker independently reads backticked IDs from the first column of every
Part B and Part D Markdown table. Composite cells therefore produce one ID per
backticked token. It also reads literal, non-wildcard ``cost.*`` IDs from the
HDEV-input column of D9a. Repeated references and wildcard tokens are not new
inputs.

Status policy recorded by the UX registers
-------------------------------------------
Every register uses one exact canonical maturity: FINAL, WIP, DESIGNED,
PLANNED, PROPOSED, OPEN, or PARKED. Field maturity and default behaviour are
independent: explicit Part B defaults remain Python-owned, marked prefills even
when another aspect of that field is unresolved. Only unresolved default choices
remain unselected, and Part D COWI spreadsheet samples remain illustrative.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable

REQUIRED_COLUMNS = [
    "id",
    "map_status",
    "label",
    "help_text",
    "page",
    "section",
    "tier",
    "container",
    "control",
    "options",
    "unit_ui",
    "unit_switch",
    "default_behaviour",
    "required",
    "validation",
    "appears_when",
    "closes_when",
    "fills",
    "views",
    "start_points",
    "scenario_lever",
    "year8_related",
    "reason",
]

ALLOWED_STATUSES = {
    "FINAL",
    "WIP",
    "DESIGNED",
    "PLANNED",
    "PROPOSED",
    "OPEN",
    "PARKED",
}

CANONICAL_PAGES = {
    "Setup / Start and purpose",
    "Duties / Fleet groups",
    "Duties / Vehicle",
    "Duties / Route and stops",
    "Duties / Load and body equipment",
    "Duties / Schedule and calendar",
    "Conditions / Weather and cab climate",
    "Energy chain / Battery and ageing",
    "Energy chain / Charging",
    "Site / Depot and grid",
    "Site / Flexibility",
    "Business case / Prices and tariffs",
    "Business case / Costs and finance",
    "Business case / Taxes and CO2",
    "Business case / Tender and bids",
    "Setup / Scenarios",
}

ALLOWED_TIERS = {
    "always visible",
    "one step away",
    "expert view",
    "never shown; available in Inputs and sources ledger",
}

ID_RE = re.compile(r"`([a-z][a-z0-9_]*\.[a-z0-9_*]+)`")
DP_RE = re.compile(r"\bDP-(?:09|10|11|12|13|14|15|16)\b")
LOCK_SINGLE_RE = re.compile(r"\b(?:Rule|Rules)\s+(\d+)\b")
LOCK_RANGE_RE = re.compile(r"\bRules\s+(\d+)[–-](\d+)\b")


def _map_parts(text: str) -> tuple[str, str]:
    """Return Parts B and D, failing clearly if map boundaries move."""
    try:
        part_b = text.split("# PART B.", 1)[1].split("# PART C.", 1)[0]
        part_d = text.split("# PART D.", 1)[1].split("# PART E.", 1)[0]
    except IndexError as exc:
        raise ValueError(
            "map must contain PART B, PART C, PART D, and PART E headings"
        ) from exc
    return part_b, part_d


def _markdown_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def expected_input_ids(map_path: Path) -> list[str]:
    """Derive the ordered unique input inventory required by the UX brief."""
    text = map_path.read_text(encoding="utf-8")
    part_b, part_d = _map_parts(text)
    found: list[str] = []

    # The brief defines an input as a backticked ID in the first table column.
    # Multiple tokens split composite definitions such as sch.out / sch.back.
    for part in (part_b, part_d):
        for line in part.splitlines():
            if not line.startswith("|"):
                continue
            first_column = _markdown_cells(line)[0]
            found.extend(
                value for value in ID_RE.findall(first_column) if "*" not in value
            )

    # D9a is the one exception: its input IDs live in the third column.
    try:
        d9a = part_d.split("**D9a.", 1)[1].split("**D9b.", 1)[0]
    except IndexError as exc:
        raise ValueError("map Part D must contain D9a and D9b markers") from exc

    for line in d9a.splitlines():
        if not line.startswith("|"):
            continue
        cells = _markdown_cells(line)
        if len(cells) < 3:
            continue
        found.extend(
            value
            for value in ID_RE.findall(cells[2])
            if value.startswith("cost.") and "*" not in value
        )

    # References and repeated definitions do not create extra required rows.
    return list(dict.fromkeys(found))


def _duplicates(values: Iterable[str]) -> list[str]:
    counts = Counter(values)
    return sorted(value for value, count in counts.items() if count > 1)


def _find_header(
    normalized: dict[str, str], aliases: tuple[str, ...]
) -> str | None:
    return next((normalized[alias] for alias in aliases if alias in normalized), None)


def check_lock_rules(path: Path) -> tuple[list[str], str]:
    """If present, verify exact-one coverage and usable rule semantics 1–68."""
    if not path.exists():
        return [], "not checked (lock_rules_ux.csv not found)"

    errors: list[str] = []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        normalized = {header.strip().lower(): header for header in headers}

        rule_key = _find_header(
            normalized, ("rule", "rule_number", "number", "id")
        )
        status_key = _find_header(normalized, ("map_status",))
        if status_key is None:
            errors.append("lock_rules_ux.csv has no map_status column")
        semantic_aliases = {
            "screen": ("screen", "page"),
            "trigger": ("trigger_control", "trigger"),
            "appears": ("appears", "what_appears", "opens"),
            "disappears": ("disappears", "what_disappears", "closes"),
            "animation": ("animation",),
            "closed-value policy": (
                "typed_value_policy",
                "closed_value_behaviour",
                "closed_value_behavior",
            ),
        }
        resolved: dict[str, str] = {}
        for meaning, aliases in semantic_aliases.items():
            key = _find_header(normalized, aliases)
            if key is None:
                errors.append(f"lock_rules_ux.csv has no {meaning} column")
            else:
                resolved[meaning] = key

        if rule_key is None:
            errors.append(
                "lock_rules_ux.csv has no rule/rule_number/number/id column"
            )
            return errors, "checked"

        rule_numbers: list[int] = []
        for line_number, row in enumerate(reader, 2):
            raw_rule = (row.get(rule_key) or "").strip()
            if status_key is not None:
                status = (row.get(status_key) or "").strip()
                if status not in ALLOWED_STATUSES:
                    errors.append(
                        f"lock row {line_number} ({raw_rule or 'unknown rule'}): "
                        f"invalid map_status {status!r}"
                    )
            match = re.search(r"\d+", raw_rule)
            if not match:
                errors.append(
                    f"lock row {line_number}: invalid rule number {raw_rule!r}"
                )
                continue
            rule_numbers.append(int(match.group()))
            for meaning, key in resolved.items():
                if not (row.get(key) or "").strip():
                    errors.append(f"lock row {line_number}: blank {meaning}")

    counts = Counter(rule_numbers)
    missing = [number for number in range(1, 69) if counts[number] == 0]
    duplicated = [number for number in range(1, 69) if counts[number] > 1]
    outside = sorted(number for number in counts if number not in range(1, 69))
    if missing:
        errors.append("lock rules missing: " + ", ".join(map(str, missing)))
    if duplicated:
        errors.append("lock rules duplicated: " + ", ".join(map(str, duplicated)))
    if outside:
        errors.append("lock rules outside 1–68: " + ", ".join(map(str, outside)))
    return errors, "checked"


def check_menu_map(path: Path) -> tuple[list[str], str]:
    """If present, validate menu-map statuses without coupling its parser."""
    if not path.exists():
        return [], "not checked (menu_map.csv not found)"

    errors: list[str] = []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        normalized = {header.strip().lower(): header for header in headers}
        status_key = _find_header(normalized, ("map_status",))
        menu_key = _find_header(normalized, ("menu",))
        item_key = _find_header(normalized, ("item",))

        if status_key is None:
            errors.append("menu_map.csv has no map_status column")
            return errors, "checked"

        for line_number, row in enumerate(reader, 2):
            status = (row.get(status_key) or "").strip()
            if status in ALLOWED_STATUSES:
                continue
            menu = (row.get(menu_key) or "").strip() if menu_key else ""
            item = (row.get(item_key) or "").strip() if item_key else ""
            identity = " / ".join(value for value in (menu, item) if value)
            errors.append(
                f"menu row {line_number} ({identity or 'unknown item'}): "
                f"invalid map_status {status!r}"
            )

    return errors, "checked"


def check_register(
    map_path: Path, csv_path: Path, lock_path: Path, menu_path: Path
) -> int:
    expected = expected_input_ids(map_path)
    expected_set = set(expected)

    with csv_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        rows = list(reader)

    column_errors: list[str] = []
    if headers != REQUIRED_COLUMNS:
        missing_columns = [name for name in REQUIRED_COLUMNS if name not in headers]
        extra_columns = [name for name in headers if name not in REQUIRED_COLUMNS]
        if missing_columns:
            column_errors.append("missing columns: " + ", ".join(missing_columns))
        if extra_columns:
            column_errors.append("extra columns: " + ", ".join(extra_columns))
        if not missing_columns and not extra_columns:
            column_errors.append("columns are not in the required order")

    ids = [(row.get("id") or "").strip() for row in rows]
    ids_set = set(ids)
    duplicates = _duplicates(ids)
    missing = [value for value in expected if value not in ids_set]
    unexpected = sorted(value for value in ids_set if value and value not in expected_set)

    status_errors: list[str] = []
    row_errors: list[str] = []
    referenced_rules: set[int] = set()

    for line_number, row in enumerate(rows, 2):
        value = (row.get("id") or "").strip() or f"line {line_number}"
        status = (row.get("map_status") or "").strip()
        if status not in ALLOWED_STATUSES:
            status_errors.append(f"{value}: {status!r}")

        for column in REQUIRED_COLUMNS:
            if not (row.get(column) or "").strip():
                row_errors.append(f"{value}: blank {column}")

        page = (row.get("page") or "").strip()
        if page not in CANONICAL_PAGES:
            row_errors.append(f"{value}: non-canonical page {page!r}")

        tier = (row.get("tier") or "").strip()
        if tier not in ALLOWED_TIERS:
            row_errors.append(f"{value}: unsupported tier {tier!r}")

        if (row.get("scenario_lever") or "").strip() not in {"yes", "no"}:
            row_errors.append(f"{value}: scenario_lever must be yes/no")
        if (row.get("year8_related") or "").strip() not in {"yes", "no"}:
            row_errors.append(f"{value}: year8_related must be yes/no")

        reason = row.get("reason") or ""
        if "[MAP]" not in reason or not DP_RE.search(reason):
            row_errors.append(
                f"{value}: reason must cite literal [MAP] and DP-09–DP-16"
            )

        views = row.get("views") or ""
        for audience in ("client", "OEM", "engineering"):
            if audience not in views:
                row_errors.append(f"{value}: views does not account for {audience}")

        start_points = row.get("start_points") or ""
        starts = {int(number) for number in re.findall(r"\b([1-5])\b", start_points)}
        if not starts:
            row_errors.append(f"{value}: start_points must reference 1–5")

        default = row.get("default_behaviour") or ""
        if status in {"OPEN", "PROPOSED", "PARKED"} and default.startswith(
            "Pre-filled"
        ):
            row_errors.append(
                f"{value}: unresolved status must not become a pre-filled default"
            )
        if "COWI sample" in default and default.startswith("Pre-filled"):
            row_errors.append(f"{value}: COWI sample must remain illustrative")

        lock_text = " ".join(
            row.get(name, "") or ""
            for name in ("appears_when", "closes_when", "fills")
        )
        referenced_rules.update(
            int(number) for number in LOCK_SINGLE_RE.findall(lock_text)
        )
        for start, end in LOCK_RANGE_RE.findall(lock_text):
            first, last = int(start), int(end)
            if first <= last:
                referenced_rules.update(range(first, last + 1))

    missing_rule_refs = [
        number for number in range(1, 69) if number not in referenced_rules
    ]
    if missing_rule_refs:
        row_errors.append(
            "inputs register does not reference lock rules: "
            + ", ".join(map(str, missing_rule_refs))
        )

    lock_errors, lock_status = check_lock_rules(lock_path)
    all_errors = column_errors + status_errors + row_errors + lock_errors

    print("UX input coverage check")
    print(f"Map: {map_path}")
    print(f"CSV: {csv_path}")
    print(
        "Inference policy: untagged Part B consumption-facing inputs are WIP; "
        "a more specific explicit field/section status overrides WIP; D9a "
        "inherits PLANNED. OPEN/PROPOSED/PARKED choices remain unresolved and "
        "never become defaults."
    )
    print(f"Expected input IDs: {len(expected)}")
    print(f"CSV rows: {len(rows)}")
    print(
        f"Missing IDs: {len(missing)}"
        + (f" — {', '.join(missing)}" if missing else "")
    )
    print(
        f"Duplicate IDs: {len(duplicates)}"
        + (f" — {', '.join(duplicates)}" if duplicates else "")
    )
    print(
        f"Unexpected IDs: {len(unexpected)}"
        + (f" — {', '.join(unexpected)}" if unexpected else "")
    )
    print(f"Allowed status violations: {len(status_errors)}")
    print(f"Required column errors: {len(column_errors)}")
    print(f"Row contract errors: {len(row_errors)}")
    print(
        f"Lock rules: {lock_status}"
        + (f"; errors: {len(lock_errors)}" if lock_status == "checked" else "")
    )

    if all_errors:
        print("Errors:")
        for error in all_errors:
            print(f"- {error}")
        print("RESULT: FAIL")
        return 1

    print("RESULT: PASS")
    return 0


def main() -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Check exact UX-input coverage against hdev-input-map.md"
    )
    parser.add_argument(
        "--map",
        type=Path,
        default=here.parents[1] / "design" / "hdev-input-map.md",
        help="authoritative Markdown input map",
    )
    parser.add_argument(
        "--inputs",
        type=Path,
        default=here / "inputs_ux.csv",
        help="UX input register to check",
    )
    parser.add_argument(
        "--lock-rules",
        type=Path,
        default=here / "lock_rules_ux.csv",
        help="optional lock-rule register",
    )
    args = parser.parse_args()

    try:
        return check_register(
            args.map.resolve(), args.inputs.resolve(), args.lock_rules.resolve()
        )
    except (OSError, UnicodeError, csv.Error, ValueError) as exc:
        print("UX input coverage check")
        print(f"ERROR: {exc}")
        print("RESULT: FAIL")
        return 1


if __name__ == "__main__":
    sys.exit(main())
