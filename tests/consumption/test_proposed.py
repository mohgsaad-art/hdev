"""Q12 and Part I tests: the proposal equals the code of record where it should, and differs only where intended.  ILLUSTRATIVE numbers."""
import numpy as np
import pytest

import reference_copy as RC
from _synth import base_args, old_call, rows


def test_kelvin_and_ms_inside_give_the_same_numbers_as_celsius_and_kmh_inside():
    """[TEST] Q12: removing '+ 273.15' and '* 3.6' from the engine changes nothing numerically (zero rotor, ideal drivetrain, no PTO)."""
    a = base_args(rows(), aux=(1000, 200, 250, 20, 600, 0), eff=(1.0, 1.0, 1.0), v_no_regen=-1.0)
    old = old_call(a, regen_effeiciency=1.0)
    new = RC.consumption_engine_v_proposed(**a)
    assert np.allclose(new["P_wheel"], old[0], rtol=1e-12, atol=1e-9)
    assert np.allclose(new["P_battery"], old[3], rtol=1e-12, atol=1e-9)
    assert new["E_battery"] == pytest.approx(old[4], rel=1e-12)


def test_split_eff_with_default_switches_is_the_proposal():
    a = base_args(rows(), aux=(1000, 200, 250, 20, 600, 0), eff=(0.98, 0.95, 0.95), v_no_regen=5 / 3.6, J_rotor=0.45, i_total=10.0)
    p = RC.consumption_engine_v_proposed(**a)
    s = RC.consumption_engine_v_split_eff(**a)
    assert np.allclose(p["P_battery"], s["P_battery"]) and p["E_battery"] == pytest.approx(s["E_battery"])


def test_proposal_uses_the_same_signs_as_the_code_of_record_when_rotor_and_pto_are_off():
    """With scalar efficiencies, rotor 0 and no PTO the only difference is: regen uses gearbox x motor x inverter (symmetric) instead of one number."""
    a = base_args(rows(), eff=(0.98, 0.95, 0.95), v_no_regen=5 / 3.6)
    old = old_call(a, regen_effeiciency=0.98 * 0.95 * 0.95)
    new = RC.consumption_engine_v_proposed(**a)
    assert new["E_battery"] == pytest.approx(old[4], rel=1e-12)


def test_proposal_returns_the_energy_split_the_battery_engine_needs():
    a = base_args(rows(), aux=(1000, 200, 250, 20, 600, 0), eff=(0.98, 0.95, 0.95))
    p = RC.consumption_engine_v_proposed(**a)
    assert p["E_battery"] == pytest.approx(p["E_drive"] + p["E_regen"] + p["E_aux"], rel=1e-12)
    assert p["E_regen"] <= 0 <= p["E_drive"]
