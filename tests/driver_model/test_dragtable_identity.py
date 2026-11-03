"""Assert driver_model_v_dragtable reproduces the code of record exactly with a zero
drag table (and with P_drag_loss=0). This proves any D2 difference comes only from the
drag table, not a transcription slip in the variant."""
import numpy as np
import pytest

from tests.driver_model.reference_copy import driver_model
from tests.driver_model.driver_model_v_dragtable import driver_model_dragtable
from tests.driver_model import _vecto_data as D
from tests.driver_model import _vecto_vehicle as VV

VACC = D.load_vacc()
CYCLES = sorted(D.list_cycles())


@pytest.mark.skipif(not CYCLES, reason="no cycles")
@pytest.mark.parametrize("cyc", CYCLES)
def test_zero_drag_table_identical_to_code_of_record(cyc):
    s, v, grad, stop = D.load_cycle(D.list_cycles()[cyc])
    kw = dict(coast_mass=VV.M_REF, m_red_wheels=VV.M_RED_WHEELS,
              cdxa_v=list(VV.CDXA_V), cdxa=list(VV.CDXA_REF),
              Crr=VV.crr_total_vecto(VV.M_REF), rho=VV.RHO_VECTO, g=VV.G)
    ref = driver_model(s, v, stop, grad, *VACC, P_drag_loss=0.0, **kw)
    var = driver_model_dragtable(s, v, stop, grad, *VACC,
                                 drag_v_kmh=(0.0, 1000.0), drag_f=(0.0, 0.0), **kw)
    for a, b, name in zip(ref, var, ["T", "S", "V", "A", "grade", "M"]):
        assert len(a) == len(b), f"{cyc} {name}: length differs"
        assert np.allclose(np.asarray(a, float), np.asarray(b, float), atol=1e-9), \
            f"{cyc} {name}: differs"
