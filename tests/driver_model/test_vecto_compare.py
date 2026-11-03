"""Part D regression — code of record vs the real VECTO 5.1.6-RC .vmod.

Pins the headline Part D metrics so a future change to the code of record that moves
the HDEV-vs-VECTO agreement is caught. Uses the generic-E2 reference vehicle from
harness v1.7 (_vecto_vehicle.py) and the .vmod files in docs/research/vecto/.

Skips cleanly if the .vmod files are not present.
"""
import os

import numpy as np
import pytest

from tests.driver_model.reference_copy import driver_model
from tests.driver_model import _vecto_data as D
from tests.driver_model import _vecto_vehicle as VV
from tests.driver_model import _vmod as VM


RUN_TO_CYCLE = {
    "BEV_E2_RegionalDelivery_ReferenceLoad_1Hz": "RegionalDelivery",
    "BEV_E2_UrbanDelivery_ReferenceLoad_1Hz": "UrbanDelivery",
    "BEV_E2_LongHaul_ReferenceLoad_1Hz": "LongHaul",
}

RUNS = VM.run_files()
VACC_V, VACC_ACC, VACC_DEC = D.load_vacc()

# expected RMS speed agreement (km/h) — generous upper bounds around measured values
RMS_MAX = {
    "RegionalDelivery": 1.6,
    "UrbanDelivery": 2.4,
    "LongHaul": 2.0,
}


def _have(run):
    return run in RUNS


@pytest.mark.skipif(not RUNS, reason="no VECTO .vmod files present")
class TestVectoCompare:
    @pytest.mark.parametrize("run,cyc", list(RUN_TO_CYCLE.items()))
    def test_speed_rms_vs_vecto(self, run, cyc):
        if not _have(run):
            pytest.skip(f"{run} missing")
        cols = VM.load_vmod(RUNS[run])
        dist_v = VM.col(cols, "dist")
        v_v = VM.col(cols, "v_act")
        s, v, grad, stop = D.load_cycle(D.list_cycles()[cyc])
        T, S, V, A, gr, M = driver_model(
            s, v, stop, grad, VACC_V, VACC_ACC, VACC_DEC, **VV.driver_kwargs())
        s_max = min(S[-1], dist_v[-1])
        grid = np.arange(0, s_max, 10.0)
        diff = np.interp(grid, S, V) * 3.6 - np.interp(grid, dist_v, v_v)
        rms = float(np.sqrt(np.mean(diff ** 2)))
        assert rms < RMS_MAX[cyc], f"{cyc}: speed RMS {rms:.3f} km/h > {RMS_MAX[cyc]}"

    @pytest.mark.parametrize("run,cyc", list(RUN_TO_CYCLE.items()))
    def test_standing_rows_match_vecto(self, run, cyc):
        if not _have(run):
            pytest.skip(f"{run} missing")
        cols = VM.load_vmod(RUNS[run])
        da = VM.col(cols, "DriverAction").astype(int)
        s, v, grad, stop = D.load_cycle(D.list_cycles()[cyc])
        T, S, V, A, gr, M = driver_model(
            s, v, stop, grad, VACC_V, VACC_ACC, VACC_DEC, **VV.driver_kwargs())
        vecto_halt = int((da == 0).sum())
        hdev_stop = int((M == 0).sum())
        # standing rows match VECTO exactly (resolves the 2.3 standing-time worry)
        assert hdev_stop == vecto_halt, f"{cyc}: HDEV stop {hdev_stop} != VECTO Halt {vecto_halt}"

    @pytest.mark.parametrize("run,cyc", list(RUN_TO_CYCLE.items()))
    def test_hdev_coasts_more_than_vecto(self, run, cyc):
        """Documents the known coast-gap (HDEV > VECTO with P_drag_loss=0). This is the
        #1 finding; the test pins its DIRECTION so a drag-table change that closes it
        is noticed."""
        if not _have(run):
            pytest.skip(f"{run} missing")
        cols = VM.load_vmod(RUNS[run])
        da = VM.col(cols, "DriverAction").astype(int)
        vecto_coast = float(((da == 4) | (da == 2)).mean()) * 100
        s, v, grad, stop = D.load_cycle(D.list_cycles()[cyc])
        T, S, V, A, gr, M = driver_model(
            s, v, stop, grad, VACC_V, VACC_ACC, VACC_DEC, **VV.driver_kwargs())
        hdev_coast = float((M == 3).mean()) * 100
        assert hdev_coast > vecto_coast, (cyc, hdev_coast, vecto_coast)
