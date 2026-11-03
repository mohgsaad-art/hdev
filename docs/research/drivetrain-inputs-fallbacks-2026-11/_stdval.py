"""Standard-value drivetrain + coasting-drag model for the fallback tests
(drivetrain-inputs-fallbacks, 3 Nov 2026).

TEST-ONLY. Nothing here is in Bob's engine (src/engine/*). This is a faithful,
self-contained re-build of the 22 Oct add-on (docs/research/vecto/
hdev_addon_std_drag_v1.py) so the Part-D fallback sweeps can run in CI without
the live Colab notebook. Every formula carries a source tag.

Sources (read directly, not from memory):
  gearbox std loss  : Reg. (EU) 2017/2400 Annex VI App. 8 (AMT), as used in the
                      22 Oct test [TEST hdev_addon_std_drag_v1.py]:
                        T_loss,in = Td0 + Td1000*n/1000 + fT*|T_in|
                        Td0 = Td1000 = 0.005*Tmax_in ; fT = 0.04 indirect / 0.01 direct
  axle std loss     : two options, selectable (see AxleFormula):
      "reg70"  : Td0 = 70 + 20*i_axle (constant), eta 0.98   [TEST 22 Oct add-on]
      "vecto"  : VECTO generic axle, read at commit b8d6126:
                 GenericTransmissionComponentData.cs 71-124 + Constants.cs 403-417
                 Td0 = 52.5 + 15*i ; split half fixed + half*(n_out/150) ; |T|/0.98-|T|
  motor eff/drag    : Annex Xb App. 8 steps 6-7 (k_mn ASM table, x0.96, drag curve)
                      [TEST 22 Oct add-on std_motor / std_motor_drag]
  loss-map lookup   : VECTO TransmissionLossMap (Delaunay + nearest fallback)
  E2 truth values   : VECTO Generic Vehicles/Declaration Mode/PEV/GenericVehicleE2
                      (AMT.vgbx gears 3.86/1.93, axle 2.59; BatteryElectricVehicle.vveh
                       2 motors, ADC 2.0; GenericEMotor_125kW_485Nm.vemp 485 Nm,
                       rated 2461.16 rpm, max 9845 rpm) [VECTO b8d6126]
  r_dyn             : Wheels.cs DynamicTyreRadius = d * f / (2*pi); 265/70 R19.5
                      d=867 mm, f=3.05 -> 0.42086 m [VECTO b8d6126 Wheels.cs + Wheels.csv]
Flags carried through:
  [ASSUMP] Tmax_in = N_EM * T_EM_MAX * I_ADC = 2*485*2.0 = 1940 Nm (no published source)
  [ASSUMP] coasting drag uses a single fixed gear (gear 2); ADC loss 0 as in the .vmod;
           rotor inertia ignored.
"""
import math
import os

import numpy as np
from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator

RPM = 60 / (2 * math.pi)

# ---- E2 truth values [VECTO b8d6126] ----
I_AXLE = 2.59                       # AMT.vgbx first "Gears" entry (axlegear slot)
I_GEAR = {1: 3.86, 2: 1.93}         # AMT.vgbx gears 1, 2
I_ADC = 2.0                         # BatteryElectricVehicle.vveh motor-to-gearbox ratio
N_EM = 2                            # two motors
T_EM_MAX = 485.0                    # GenericEMotor_125kW_485Nm.vemp T_drive max
N_RATED = 2461.158914              # rated speed (per motor) rpm
N_EM_MAX = 9845.0                   # max motor speed rpm
R_DYN = 0.867 * 3.05 / (2 * math.pi)  # Wheels.cs; 265/70 R19.5 -> 0.42086 m

# [ASSUMP] gearbox max input torque
TMAX_IN_TRUTH = N_EM * T_EM_MAX * I_ADC   # 1940 Nm


# ---------------- loss map helper (VECTO-style input-side lookup) --------------
class _Loss:
    """Torque-loss map keyed on (input speed, input torque). Built from an
    output-side (n_out, T_out, loss) table; converts to input side like VECTO."""
    def __init__(self, m, ratio):
        self.ratio = ratio
        pts = np.c_[m[:, 0], m[:, 1] - m[:, 2]]
        self.lin = LinearNDInterpolator(pts, m[:, 2])
        self.near = NearestNDInterpolator(pts, m[:, 2])

    def input_side(self, n_out, T_out):
        n_in, T = n_out * self.ratio, T_out / self.ratio
        loss = self.lin(n_in, T)
        bad = np.isnan(loss)
        loss[bad] = self.near(n_in[bad], T[bad])
        return n_in, T + loss, loss


# ---------------- gearbox std value [Annex VI App. 8] -------------------------
def std_gearbox(ratio, tmax_in, fT=0.04):
    td = 0.005 * tmax_in                       # Td0 = Td1000
    n = np.array([0, 250, 500, 750, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 5000, 6000], float)
    N, TT = np.meshgrid(n, np.linspace(-1.1 * tmax_in, 1.1 * tmax_in, 45))
    N, TT = N.ravel(), TT.ravel()
    loss = td + td * N / 1000 + fT * np.abs(TT)
    return _Loss(np.c_[N, TT, loss], ratio), td, fT


# ---------------- axle std value: two formulas --------------------------------
def std_axle_reg70(ratio, T0=70.0, T1=20.0, eta=0.98):
    """22 Oct formula: Td0 = 70 + 20*i (constant), |T|/eta-|T|. [TEST 22 Oct]"""
    td0 = T0 + T1 * ratio
    n_out = np.array([0, 50, 100, 200, 400, 600, 800, 1000, 1500, 2000, 3000, 5000], float)
    T_out = np.r_[-np.geomspace(250, 500000, 25)[::-1], 0, np.geomspace(250, 500000, 25)]
    N, TT = np.meshgrid(n_out, T_out)
    N, TT = N.ravel(), TT.ravel()
    lo = td0 + np.abs(TT) / eta - np.abs(TT)
    return _Loss(np.c_[N * ratio, (TT + lo) / ratio, lo / ratio], ratio), td0, 0.0, eta


def std_axle_vecto(ratio, T0=52.5, T1=15.0, td_n=150.0, eta=0.98):
    """VECTO generic axle [GenericTransmissionComponentData.cs 71-124 + Constants.cs 403-417].
    Td0 = 52.5 + 15*i ; half fixed + half*(n_out/150) + |T|/0.98-|T|."""
    td0 = T0 + T1 * ratio
    td0_ = td0 * 0.5
    td150_ = td0 * 0.5
    n_out = np.array([0, 50, 100, 200, 400, 600, 800, 1000, 1500, 2000, 3000, 5000], float)
    T_out = np.r_[-np.geomspace(250, 500000, 25)[::-1], 0, np.geomspace(250, 500000, 25)]
    N, TT = np.meshgrid(n_out, T_out)
    N, TT = N.ravel(), TT.ravel()
    calc_n = np.where(N == 0, 50.0, N)          # VECTO uses OutputSpeedStart=50 at n=0
    lo = td0_ + td150_ * calc_n / td_n + np.abs(TT) / eta - np.abs(TT)
    return _Loss(np.c_[N * ratio, (TT + lo) / ratio, lo / ratio], ratio), td0_, td150_, eta


# ---------------- motor std value [Annex Xb App. 8 steps 6-7] -----------------
K_ASM = {(2, 0): 0.1, (2, 1): 0.03, (2, 2): 0.03, (1, 0): 0.01, (1, 2): 0.001,
         (0, 0): 0.003, (0, 2): 0.001, (0, 3): 0.001}


def _std_eff(Tn, Wn):
    pl = sum(c * np.abs(Tn) ** m * np.abs(Wn) ** n for (m, n), c in K_ASM.items())
    pm = Tn * Wn
    return np.maximum(np.where(Tn > 0, pm / (pm + pl), (pm + pl) / pm) * 0.96, 0)


def std_motor():
    wn = np.r_[0.02, np.arange(0.2, 4.0001, 0.2)]
    tn = np.r_[-np.arange(1.0, 0.0499, -0.05), -0.01, 0.01, np.arange(0.05, 1.0001, 0.05)]
    W, Tn = np.meshgrid(wn, tn)
    W, Tn = W.ravel(), Tn.ravel()
    n, T = W * N_RATED, Tn * T_EM_MAX
    Pm = T * n / RPM
    Pel = (1 - _std_eff(Tn, W)) * np.abs(Pm) + Pm
    lin = LinearNDInterpolator(np.c_[n, T], Pel)
    near = NearestNDInterpolator(np.c_[n, T], Pel)

    def f(nn, TT):
        p = lin(nn, TT)
        b = np.isnan(p)
        p[b] = near(nn[b], TT[b])
        return p
    return f


def std_motor_drag(n_rpm):
    """Annex Xb App. 8 step 7: drag torque per motor at Tn=0.01, wn=1 and 4,
    linear in/out [TEST 22 Oct]."""
    d1, d4 = [(1 - _std_eff(np.array(0.01), np.array(wn))) * 0.01 * T_EM_MAX for wn in (1.0, 4.0)]
    return d1 + (d4 - d1) * (np.asarray(n_rpm, float) - N_RATED) / (3 * N_RATED)


# ---------------- full standard-value drivetrain object -----------------------
_VECTO_SRC = os.environ.get("VECTO_SRC", "/projects/sandbox/vecto-src")


def _read_fld():
    """E2 full-load curve (per motor) n, T_drive, T_drag from the .vemp."""
    path = os.path.join(_VECTO_SRC, "Generic Vehicles", "Declaration Mode", "PEV",
                        "GenericVehicleE2", "GenericEMotor_125kW_485Nm.vemp")
    rows = []
    with open(path, encoding="latin-1") as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln or ln.lower().startswith("n "):
                continue
            p = [x.strip() for x in ln.split(",")]
            try:
                rows.append([float(p[0]), float(p[1]), float(p[2])])
            except (ValueError, IndexError):
                continue
    a = np.array(rows)
    return a[np.argsort(a[:, 0])]


class Drivetrain:
    """Standard-value E2 drivetrain. Parameters can be overridden to test fallbacks.

    All defaults are the E2 truth values; pass overrides to swap one input for a
    fallback rung (Part D4)."""

    def __init__(self, tmax_in=None, i_gear=None, i_axle=None, i_adc=None,
                 n_em=None, t_em_max=None, n_rated=None, fld=None,
                 axle_formula="vecto", r_dyn=None, drag_gear=2):
        self.tmax_in = TMAX_IN_TRUTH if tmax_in is None else tmax_in
        self.i_gear = dict(I_GEAR) if i_gear is None else dict(i_gear)
        self.i_axle = I_AXLE if i_axle is None else i_axle
        self.i_adc = I_ADC if i_adc is None else i_adc
        self.n_em = N_EM if n_em is None else n_em
        self.t_em_max = T_EM_MAX if t_em_max is None else t_em_max
        self.n_rated = N_RATED if n_rated is None else n_rated
        self.r_dyn = R_DYN if r_dyn is None else r_dyn
        self.axle_formula = axle_formula
        self.drag_gear = drag_gear

        self.gb = {}
        self.gb_td = {}
        self.gb_fT = {}
        for g, ratio in self.i_gear.items():
            # gear 1 (highest ratio) treated as indirect (fT 0.04); top gear direct-ish
            fT = 0.04
            L, td, ft = std_gearbox(ratio, self.tmax_in, fT=fT)
            self.gb[g] = L
            self.gb_td[g] = td
            self.gb_fT[g] = ft
        if axle_formula == "reg70":
            self.ax, self.ax_td0, self.ax_td150, self.ax_eta = std_axle_reg70(self.i_axle)
        else:
            self.ax, self.ax_td0, self.ax_td150, self.ax_eta = std_axle_vecto(self.i_axle)
        self.emf = std_motor()
        _fld = _read_fld() if fld is None else fld
        self._fld = _fld
        self.t_drive_max = lambda n: np.interp(n, _fld[:, 0], _fld[:, 1])
        self.t_gen_max = lambda n: np.interp(n, _fld[:, 0], np.abs(_fld[:, 2]))

    # ---- wheel power -> electric power of all motors [W] ----
    def electric_power(self, v_avg, P_wheel, use, v_no_regen=0.0):
        n = len(v_avg)
        P_el = np.zeros(n)
        parts = dict(axle=np.zeros(n), gearbox=np.zeros(n), motor=np.zeros(n),
                     friction_brake=np.zeros(n))
        gear_used = np.zeros(n, int)
        w = v_avg / self.r_dyn
        on = use & (w > 1e-3) & (P_wheel != 0)
        if not on.any():
            return P_el, parts, gear_used
        n_ax, T_ax, l_ax = self.ax.input_side(w[on] * RPM, P_wheel[on] / w[on])
        res = {}
        for g, L in self.gb.items():
            n_gb, T_gb, l_gb = L.input_side(n_ax, T_ax)
            res[g] = (n_gb, T_gb, l_gb, n_gb * self.i_adc, T_gb / self.i_adc / self.n_em)
        gears = sorted(self.i_gear)
        g_hi = gears[-1]            # smallest ratio -> "gear 2"
        g_lo = gears[0]
        ok_hi = (res[g_hi][4] <= self.t_drive_max(res[g_hi][3])) & (res[g_hi][3] <= N_EM_MAX)
        ok_lo = res[g_lo][3] <= N_EM_MAX
        g_sel = np.where(ok_hi | ~ok_lo, g_hi, g_lo)
        pick = lambda k: np.where(g_sel == g_hi, res[g_hi][k], res[g_lo][k])
        n_gb, l_gb, n_em, T_em = pick(0), pick(2), pick(3), pick(4)
        cap = -self.t_gen_max(n_em)
        low = T_em < cap
        brake = np.where(low, (cap - T_em) * self.n_em * n_em / RPM, 0.0)
        T_em = np.maximum(T_em, cap)
        pe = self.emf(n_em, T_em) * self.n_em
        pm = T_em * self.n_em * n_em / RPM
        P_el[on] = pe
        gear_used[on] = g_sel
        parts["axle"][on] = l_ax * n_ax / RPM
        parts["gearbox"][on] = l_gb * n_gb / RPM
        parts["motor"][on] = pe - pm
        parts["friction_brake"][on] = np.abs(brake)
        return P_el, parts, gear_used

    # ---- coasting drag force at the wheels [N] ----
    def drag_force_old(self, v):
        """22 Oct drag: fixed gearbox Td + motor drag + axle Td0 only (NO fT*|T_in|,
        NO axle (1/eta-1)*|T|). Faithful to hdev_addon_std_drag_v1.py drag_force."""
        v = np.asarray(v, float)
        g = self.drag_gear
        n_ax = v / self.r_dyn * RPM * self.i_axle
        n_gb = n_ax * self.i_gear[g]
        n_em = n_gb * self.i_adc
        td = 0.005 * self.tmax_in
        T_gb_in = td + td * n_gb / 1000 + self.n_em * std_motor_drag(n_em) * self.i_adc
        return (T_gb_in * self.i_gear[g] * self.i_axle + self.ax_td0_constant()) / self.r_dyn

    def ax_td0_constant(self):
        """Axle fixed drag term at zero speed as the 22 Oct code used it (AX_TD0)."""
        if self.axle_formula == "reg70":
            return 70.0 + 20.0 * self.i_axle
        # vecto split: the 22 Oct code only had the constant half; expose the full td0
        return 52.5 + 15.0 * self.i_axle

    def drag_force_fixed(self, v):
        """CORRECTED drag (D2): sum the component loss POWERS and divide by speed,
        exactly as VECTO does (gearboxLoss + axleLoss + emDrag)/v, with each loss read
        at the operating point the drag itself produces [VECTO DefaultDriverStrategy.cs
        764-769]. The 22 Oct table (drag_force_old) kept only the fixed Td terms and
        the motor drag; it DROPPED the gearbox fT*|T_in| term and the axle
        (1/eta-1)*|T| term, and (for the VECTO axle) the speed-dependent half. This
        rebuild puts those back.

        Torque chain, starting at the wheel resistance F (unknown) and working to the
        motor, is implicit; here we build it from the motor-drag source outward, since
        during a pure coast the only driving torque is the component drag itself."""
        v = np.asarray(v, float)
        g = self.drag_gear
        w_wheel = np.maximum(v / self.r_dyn, 1e-6)          # wheel speed [rad/s]
        n_ax_in = w_wheel * self.i_axle * RPM               # axle input speed [rpm]
        w_ax_in = w_wheel * self.i_axle                     # [rad/s]
        n_gb_in = n_ax_in * self.i_gear[g]                  # gearbox input speed [rpm]
        w_gb_in = w_ax_in * self.i_gear[g]                  # [rad/s]
        n_em = n_gb_in * self.i_adc                         # motor speed [rpm]

        # 1) motor drag torque per all motors, referred to the gearbox input [Nm]
        T_motor_drag_gb = self.n_em * std_motor_drag(n_em) * self.i_adc
        em_drag_power = T_motor_drag_gb * w_gb_in           # [W] (ADC loss ignored, as .vmod)

        # 2) gearbox loss power: loss torque at the gearbox input, through the shaft
        #    at w_gb_in. T_in = the drag torque flowing through it.
        td = 0.005 * self.tmax_in
        fT = self.gb_fT[g]
        gb_loss_torque = td + td * n_gb_in / 1000.0 + fT * abs_(T_motor_drag_gb)
        gb_loss_power = gb_loss_torque * w_gb_in            # [W]

        # torque arriving at the axle input = (motor drag + gearbox loss) scaled by gear
        T_ax_in = (T_motor_drag_gb + gb_loss_torque) * self.i_gear[g]

        # 3) axle loss power: loss torque at the axle input (speed n_ax_in),
        #    read at the torque T_ax_in passing through.
        if self.axle_formula == "reg70":
            ax_loss_torque = (70.0 + 20.0 * self.i_axle) + abs_(T_ax_in) / 0.98 - abs_(T_ax_in)
        else:
            td0 = 52.5 + 15.0 * self.i_axle
            ax_loss_torque = (td0 * 0.5 + td0 * 0.5 * np.maximum(n_ax_in, 50.0) / 150.0
                              + abs_(T_ax_in) / 0.98 - abs_(T_ax_in))
        ax_loss_power = ax_loss_torque * w_ax_in            # [W]

        # VECTO: resistance force at the wheel = total component loss power / v
        total_loss_power = em_drag_power + gb_loss_power + ax_loss_power
        return total_loss_power / np.maximum(v, 1e-6)

    def drag_table(self, kind="fixed", vmax_kmh=130.0):
        v_tab = np.arange(0.0, vmax_kmh + 1.0, 1.0) / 3.6
        if kind == "old":
            f_tab = self.drag_force_old(v_tab)
        else:
            f_tab = self.drag_force_fixed(v_tab)
        return v_tab, f_tab


def abs_(x):
    return np.abs(x)
