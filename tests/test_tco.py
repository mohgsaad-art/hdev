# STATUS: NEW (Step 9, item 17 / 🔒 M6.24, Bob to review). TCO data-model + category-sum tests.
#
# These assert the DATA MODEL (six client-facing categories, to-be-sourced slots) and the ONLY
# arithmetic this module does (category sums), and that NO price/coefficient is hard-coded: every
# method coefficient slot and the empty model's line items are None (locked). Headline metrics are
# locked by M6.24 and must return None.
import json

from src.server import tco


def test_category_names_are_the_six_client_facing():
    assert tco.CATEGORY_NAMES == (
        "Owning", "Running", "Infrastructure", "Policy & taxes", "Hidden costs", "Climate",
    )


def test_empty_model_has_all_categories_and_no_numbers():
    model = tco.empty_tco_model()
    assert [c["name"] for c in model["categories"]] == list(tco.CATEGORY_NAMES)
    # every method coefficient slot is None and locked (no COWI number baked in).
    for key, slot in model["method_slots"].items():
        assert slot["value"] is None, key
        assert slot["locked"] is True, key


def test_category_sums_sum_supplied_line_items():
    cats = [
        tco.new_category("Owning", [
            tco.new_line_item("vehicle", diesel=100.0, electric=200.0),
            tco.new_line_item("interest", diesel=10.0, electric=20.0),
        ]),
        tco.new_category("Running", [
            tco.new_line_item("fuel", diesel=50.0, electric=None),  # electric side unsourced
        ]),
        tco.new_category("Climate"),  # no line items at all -> None sums
    ]
    sums = tco.tco_category_sums(cats)
    by_name = {s["name"]: s for s in sums}
    assert by_name["Owning"]["diesel"] == 110.0
    assert by_name["Owning"]["electric"] == 220.0
    assert by_name["Running"]["diesel"] == 50.0
    assert by_name["Running"]["electric"] is None  # nothing supplied -> None, not 0
    assert by_name["Climate"]["diesel"] is None
    assert by_name["Climate"]["electric"] is None


def test_totals_across_categories():
    cats = [
        tco.new_category("Owning", [tco.new_line_item("v", diesel=100.0, electric=200.0)]),
        tco.new_category("Running", [tco.new_line_item("f", diesel=50.0, electric=None)]),
    ]
    totals = tco.tco_totals(tco.tco_category_sums(cats))
    assert totals["diesel"] == 150.0
    assert totals["electric"] == 200.0


def test_headline_metrics_locked_by_m624():
    # 🔒 M6.24: every headline metric is None until coefficients are sourced.
    metrics = tco.headline_metrics(tco.empty_tco_model())
    assert metrics["tco_per_km_dkk"] is None
    assert metrics["break_even_year"] is None
    assert metrics["monthly_cost_dkk"] is None
    assert metrics["lademeter_dkk_per_m"] is None


def test_unknown_category_name_raises():
    import pytest
    with pytest.raises(ValueError):
        tco.new_category("Not A Real Category")


def test_no_banned_internal_term_in_model_json():
    # §8: no coefficient/formula name leaks into a client-facing surface. (The slot `source` strings
    # mention design §4I by name, which is allowed - they are the provenance note, not a client string.
    # Here we check the category/line-item surface only.)
    model = tco.empty_tco_model()
    blob = json.dumps([{"name": c["name"], "line_items": c["line_items"]} for c in model["categories"]])
    for banned in ("annuity", "k_lin", "CdxA", "VECTO", "ASAP", "JIT"):
        assert banned not in blob
