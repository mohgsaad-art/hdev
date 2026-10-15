# STATUS: NEW (PR 1). Tests for the Slot class wrapping the 🔒 M6.7 shape.
from datetime import date

from src.registry import Slot, SOURCE_VALUES, is_valid_source, PROVIDED_BY_VOCAB


def test_empty_slot_defaults():
    s = Slot.empty()
    assert s.value is None
    assert s.source == "missing"
    assert s.locked is False
    assert s.version == 1
    assert s.unit is None


def test_slot_has_the_eight_m6_7_fields():
    s = Slot()
    d = s.to_dict()
    assert set(d) == {"value", "unit", "source", "date", "label", "provided_by", "locked", "version"}


def test_slot_round_trips_all_fields():
    s = Slot(
        value=42,
        unit="kWh",
        source="user_edit",
        date=date(2026, 10, 12),
        label="Usable battery capacity",
        provided_by="Bob",
        locked=True,
        version=3,
    )
    d = s.to_dict()
    assert d["value"] == 42
    assert d["unit"] == "kWh"
    assert d["source"] == "user_edit"
    assert d["date"] == date(2026, 10, 12)
    assert d["label"] == "Usable battery capacity"
    assert d["provided_by"] == "Bob"
    assert d["locked"] is True
    assert d["version"] == 3


def test_is_valid_source_accepts_fixed_set():
    for src in SOURCE_VALUES:
        assert is_valid_source(src)


def test_is_valid_source_accepts_file_prefix():
    assert is_valid_source("file:client_fleet.xlsx")
    assert is_valid_source("file:note.txt")


def test_is_valid_source_rejects_garbage():
    assert not is_valid_source("nonsense")
    assert not is_valid_source("file:")  # prefix only, no filename
    assert not is_valid_source(None)
    assert not is_valid_source(123)


def test_provided_by_vocab_is_the_9_1_set():
    assert set(PROVIDED_BY_VOCAB) == {"client", "OEM", "CPO", "aggregator", "consultant", "Bob"}
