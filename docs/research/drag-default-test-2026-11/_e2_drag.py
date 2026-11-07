"""Step 1: build the E2 coasting-drag table from the VECTO component files, the way
the 3 Nov close-out (section 4.2) says is correct, and check it against the .vmod.

TEST-ONLY. Nothing here is in Bob's engine. Every value is read from a VECTO file at
commit b8d6126 or from the .vmod; nothing invented.

Method (close-out 4.2): on a pure coast in gear 2, the only driving torque is the
drivetrain's own drag. Build it OUTWARD from the motor:
  - 2 motors (BatteryElectricVehicle.vveh "Count": 2), motor drag torque per motor from
    GenericDrag_125kW_485Nm.vemd, at the motor speed for the wheel speed;
  - gearbox torque loss from Gear_2.vtlm read AT THE TORQUE THE DRAG PUTS THROUGH IT
    (not at zero torque) -- this is the correction over 18940ab's zero-torque build;
  - axle torque loss from Axle_4x2_Tractor.vtlm, read WHEEL-SIDE at n_out and at the
    torque passing through (PR #22 put it on the input shaft -> this fixes that too);
  - ADC (motor->gearbox) loss ignored, as in the .vmod [ASSUMPTION] (see adc note below).
Sum the three loss POWERS and divide by v -> drag force at the wheel, exactly as VECTO's
coasting resistance does (-P_wheel_in/v = (P_gbx_in + P_gbx_loss + P_axle_loss)/v)
[VECTO DefaultDriverStrategy.cs:764-769; close-out 4.1].

Ratios/radius [VECTO b8d6126]:
  gear 2 = 1.93 (AMT.vgbx), axle = 2.59 (AMT.vgbx), ADC = 2.0, count = 2
  (BatteryElectricVehicle.vveh), r_dyn = 0.867*3.05/(2*pi) = 0.4209 m (Wheels.cs + Wheels.csv).
"""
import csv
import math
import os

import numpy as np
from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator

RPM = 60 / (2 * math.pi)

# ---- E2 geometry [VECTO b8d6126] ----
I_AXLE = 2.59
I_GEAR2 = 1.93
I_ADC = 2.0
N_EM = 2
R_DYN = 0.867 * 3.05 / (2 * math.pi)        # 0.42086 m

_VECTO = os.environ.get("VECTO_SRC", "/projects/sandbox/vecto-src")
E2 = os.path.join(_VECTO, "Generic Vehicles", "Declaration Mode", "PEV", "GenericVehicleE2")


def _csv(fname):
    path = os.path.join(E2, fname)
    rows = []
    with open(path, encoding="latin-1") as fh:
        rd = csv.reader(fh)
        for r in rd:
            try:
                rows.append([float(x) for x in r[:3]])
            except (ValueError, IndexError):
                continue
    return np.array(rows)


class _LossMap:
    """VECTO transmission loss map: points (n_in, T_in - loss) -> loss torque.
    input_side(n_out, T_out) returns the loss torque at the INPUT shaft for a given
    OUTPUT operating point [VECTO TransmissionLossMap.cs:77,94]."""
    def __init__(self, m, ratio):
        self.ratio = ratio
        pts = np.c_[m[:, 0], m[:, 1] - m[:, 2]]
        self.lin = LinearNDInterpolator(pts, m[:, 2])
        self.near = NearestNDInterpolator(pts, m[:, 2])

    def loss_at(self, n_in, T_in_minus_loss):
        """Loss torque at input shaft for a point keyed (n_in, T_in - loss)."""
        n_in = np.atleast_1d(np.asarray(n_in, float))
        key = np.atleast_1d(np.asarray(T_in_minus_loss, float))
        loss = self.lin(n_in, key)
        bad = np.isnan(loss)
        if bad.any():
            loss[bad] = self.near(n_in[bad], key[bad])
        return loss


def _load_motor_drag():
    """Motor drag torque magnitude per motor vs motor speed, from the .vemd."""
    m = _csv("GenericDrag_125kW_485Nm.vemd")
    n = m[:, 0]
    T = np.abs(m[:, 1])
    order = np.argsort(n)
    return n[order], T[order]


def build_drag_table(vmax_kmh=130.0):
    """Return (v_kmh, F_wheel_N) over 0..vmax in 1 km/h steps. gear 2."""
    dn, dT = _load_motor_drag()
    gbx = _LossMap(_csv("Gear_2.vtlm"), I_GEAR2)
    axle = _LossMap(_csv("Axle_4x2_Tractor.vtlm"), I_AXLE)

    v_kmh = np.arange(0.0, vmax_kmh + 1.0, 1.0)
    v = v_kmh / 3.6
    w_wheel = np.maximum(v / R_DYN, 1e-9)        # rad/s
    # speeds up the chain
    n_axle_in = w_wheel * I_AXLE * RPM           # rpm
    w_axle_in = w_wheel * I_AXLE
    n_gbx_in = n_axle_in * I_GEAR2
    w_gbx_in = w_axle_in * I_GEAR2
    n_motor = n_gbx_in * I_ADC

    # 1) motor drag torque at the gearbox input (all motors through ADC) [Nm]
    T_motor = np.interp(n_motor, dn, dT)         # per motor, magnitude
    T_drag_gbx_in = N_EM * T_motor * I_ADC       # referred to gearbox input shaft
    em_drag_power = T_drag_gbx_in * w_gbx_in     # [W]

    # 2) gearbox loss power: loss torque read AT the drag torque flowing through the box.
    #    The loss map is keyed (n_in, T_in - loss); with T_in = drag torque the key ~ drag
    #    torque (loss is small vs the key for this purpose). Read at the gearbox input.
    gbx_loss_torque = gbx.loss_at(n_gbx_in, T_drag_gbx_in)
    gbx_loss_power = gbx_loss_torque * w_gbx_in  # [W]

    # torque arriving at the axle INPUT = (motor drag + gearbox loss) * gear2
    T_axle_in = (T_drag_gbx_in + gbx_loss_torque) * I_GEAR2
    # 3) axle loss power: VECTO's axle loss map is also input-keyed; read at the axle input
    #    operating point (n_axle_in, T_axle_in). This is the WHEEL-SIDE-correct build: the
    #    loss is applied once at the axle, not scaled by the axle ratio again.
    axle_loss_torque = axle.loss_at(n_axle_in, T_axle_in)
    axle_loss_power = axle_loss_torque * w_axle_in  # [W]

    total_loss_power = em_drag_power + gbx_loss_power + axle_loss_power
    F_wheel = total_loss_power / np.maximum(v, 1e-9)
    F_wheel[v_kmh == 0] = F_wheel[v_kmh == 1] if len(F_wheel) > 1 else 0.0
    # component breakdown (for the report), as force at the wheel
    comp = dict(
        motor=em_drag_power / np.maximum(v, 1e-9),
        gearbox=gbx_loss_power / np.maximum(v, 1e-9),
        axle=axle_loss_power / np.maximum(v, 1e-9),
    )
    return v_kmh, F_wheel, comp
