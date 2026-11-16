"""Reference copy of functions used in the drivetrain curve library job (16 Nov 2026).

RULES (job prompt section 1):
  * Bob's notebook and src/ are NOT edited. Everything here is a copy or a clearly named variant.
  * `drivetrain` below is Appendix A of the job prompt, copied VERBATIM (do not edit it; variants
    get a new name further down in this file).
  * Every number comes from a VECTO file (fork mohgsaad-art/VECTO, branch IEPC-experiments,
    commit b8d6126), the EEA data, or a named source. Sources are given next to the value.
"""
import numpy as np
from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator


# ======================================================================================
# APPENDIX A -- verbatim copy of `drivetrain` (job prompt 16 Nov 2026). DO NOT EDIT.
# ======================================================================================
def drivetrain(P_wheel, w_wheel, gear,                      # per row: power at the axle output [W], wheel speed [rad/s], gear (0 = no gear in)
               i_axle, axle_map,                            # axle ratio; loss map rows (input speed [rad/s], input torque [Nm], torque loss [Nm])
               i_gears, gear_maps,                          # one ratio and one loss map per gear (gear 1 = index 0)
               i_adc, eta_adc,                              # motor's own gear (ADC): ratio and efficiency
               n_em, em_map, em_T_drive, em_T_gen,          # number of motors; ONE motor's map (speed [rad/s], torque [Nm], electric power [W]); its limit curves (speed, torque)
               P_rot_rotor, P_pto_mech):                    # per row: rotor inertia power (k_rot_rotor) [W], mechanical drive PTO [W]

  P_wheel = np.asarray(P_wheel, dtype=float)
  w_wheel = np.asarray(w_wheel, dtype=float)
  gear = np.asarray(gear, dtype=int)
  P_rot_rotor = np.broadcast_to(np.asarray(P_rot_rotor, dtype=float), P_wheel.shape)
  P_pto_mech = np.broadcast_to(np.asarray(P_pto_mech, dtype=float), P_wheel.shape)
  n = len(P_wheel)

  # map lookup: linear inside the map (triangles, like VECTO's DelaunayMap); nearest map point outside it (HDEV choice, counted)
  def lookup(table, x, y):
      table = np.asarray(table, dtype=float)
      pts, val = table[:, :2], table[:, 2]
      out = LinearNDInterpolator(pts, val)(x, y)
      outside = np.isnan(out)
      out[outside] = NearestNDInterpolator(pts, val)(x[outside], y[outside])
      return out, outside

  on = (gear > 0) & (w_wheel > 1e-6)          # rows with a gear in and the wheels turning; everything else stays 0 (no gear = motor not connected)
  extrapolated = np.zeros(n, dtype=bool)

  # --- 1. axle: wheel -> axle input (VECTO AxleGear: in = out / ratio + loss, loss looked up at in-speed and out/ratio)
  T_wheel = np.zeros(n); T_wheel[on] = P_wheel[on] / w_wheel[on]
  w_ax = w_wheel * i_axle
  T_ax = T_wheel / i_axle
  loss, ext = lookup(axle_map, w_ax[on], T_ax[on])
  T_ax_in = np.zeros(n); T_ax_in[on] = T_ax[on] + loss
  extrapolated[on] |= ext

  # --- 2. gearbox: same rule, with the loss map of the gear in that row
  i_g = np.zeros(n); T_gb_in = np.zeros(n)
  for g in np.unique(gear[on]):
      r = on & (gear == g)
      i_g[r] = i_gears[g - 1]
      w_in = w_ax[r] * i_g[r]
      T_out = T_ax_in[r] / i_g[r]
      loss, ext = lookup(gear_maps[g - 1], w_in, T_out)
      T_gb_in[r] = T_out + loss
      extrapolated[np.where(r)[0][ext]] = True
  w_gb = w_ax * i_g                                           # gearbox input speed [rad/s]

  # --- 3. mechanical drive PTO sits between gearbox and motor (VECTO PEVPTO): adds torque at gearbox input speed
  T_pto = np.zeros(n); T_pto[on] = P_pto_mech[on] / w_gb[on]
  T_adc_out = T_gb_in + T_pto

  # --- 4. ADC (motor's own gear): one efficiency; driving -> divide, recovering -> multiply (VECTO CreateEmADCLossMap)
  w_em = w_gb * i_adc
  T_em = np.where(T_adc_out > 0, T_adc_out / i_adc / eta_adc, T_adc_out / i_adc * eta_adc)

  # --- 5. rotor inertia at motor speed (VECTO ElectricMotor.cs 297: map torque = shaft torque + inertia torque)
  T_rot = np.zeros(n); T_rot[on] = P_rot_rotor[on] / w_em[on]
  T_map = T_em + T_rot                                        # total torque of all motors, + = driving, - = recovering

  # --- 6. motor limits: recovering beyond the generating curve -> the rest goes to the friction brakes; driving beyond the drive curve -> flagged
  T_drive_max = n_em * np.interp(w_em, em_T_drive[0], em_T_drive[1])
  T_gen_max = n_em * np.interp(w_em, em_T_gen[0], em_T_gen[1])          # negative numbers
  over_limit = on & (T_map > T_drive_max * (1 + 1e-9))
  T_cut = np.where(on, np.maximum(T_map, T_gen_max), 0.0)
  P_to_brakes = (T_map - T_cut) * w_em                        # <= 0: recovered power the motors cannot take

  # --- 7. motor map: electric power of one motor at (speed, torque / number of motors), times the number of motors
  P_el = np.zeros(n)
  pel, ext = lookup(em_map, w_em[on], T_cut[on] / n_em)
  P_el[on] = n_em * pel
  extrapolated[np.where(on)[0][ext]] = True

  # --- 8. losses per part [W] (for the energy balance in the report)
  P_axle_loss = (T_ax_in - T_ax) * w_ax
  P_gbx_loss = (T_gb_in - T_ax_in / np.where(i_g > 0, i_g, 1)) * w_gb
  P_adc_loss = T_em * w_em - T_adc_out * w_gb
  P_em_loss = P_el - T_cut * w_em

  return P_el, P_axle_loss, P_gbx_loss, P_adc_loss, P_em_loss, P_to_brakes, extrapolated, over_limit
# ======================================================================================
# END of verbatim Appendix A
# ======================================================================================


# ======================================================================================
# Loaders for VECTO files (written for this job; units converted to SI as `drivetrain` expects)
# ======================================================================================
import os
import csv

RPM = 30.0 / np.pi          # rpm per rad/s (unit conversion, not a model number)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
VECTO_SRC = os.environ.get("VECTO_SRC", os.path.abspath(os.path.join(REPO, "..", "VECTO")))
PEV_DIR = os.path.join(VECTO_SRC, "Generic Vehicles", "Declaration Mode", "PEV")
E2_DIR = os.path.join(PEV_DIR, "GenericVehicleE2")
VMOD_DIR = os.path.join(REPO, "docs", "research", "vecto")


def _read_csv_numeric(path, ncols=3):
    rows = []
    with open(path, encoding="latin-1") as fh:
        next(fh)
        for ln in fh:
            p = [x.strip() for x in ln.strip().split(",")]
            if len(p) < ncols or not p[0]:
                continue
            rows.append([float(x) for x in p[:ncols]])
    return np.asarray(rows, dtype=float)


def read_vtlm(path):
    """VECTO transmission loss map: rpm, Nm, Nm  ->  rad/s, Nm, Nm  [VECTO TransmissionLossMapReader]."""
    a = _read_csv_numeric(path)
    a[:, 0] /= RPM
    return a


def read_vemo(path):
    """VECTO electric machine map: rpm, Nm, kW(el)  ->  rad/s, Nm, W."""
    a = _read_csv_numeric(path)
    a[:, 0] /= RPM
    a[:, 2] *= 1000.0
    return a


def read_vemp(path):
    """Full-load curve: rpm, T_drive, T_drag -> ((w, T_drive), (w, T_drag)) in SI."""
    a = _read_csv_numeric(path)
    w = a[:, 0] / RPM
    return (w, a[:, 1]), (w, a[:, 2])


def read_vmod(path):
    """VECTO .vmod: returns dict column-name(without unit) -> float array (NaN for empty)."""
    with open(path, encoding="utf-8-sig") as fh:
        lines = [ln for ln in fh if not ln.lstrip("\ufeff").startswith("#")]
    rd = list(csv.reader(lines))
    head = [h.split(" [")[0].strip() for h in rd[0]]
    cols = {h: [] for h in head}
    for r in rd[1:]:
        for h, x in zip(head, r):
            try:
                cols[h].append(float(x))
            except ValueError:
                cols[h].append(np.nan)
    return {k: np.asarray(v) for k, v in cols.items()}


def load_e2():
    """VECTO GenericVehicleE2 powertrain inputs. Ratios from the files named in the comments."""
    d = E2_DIR
    return dict(
        i_axle=2.59,                      # AMT.vgbx Gears[0].Ratio (axle), Axle_4x2_Tractor.vtlm
        i_gears=[3.86, 1.93],             # AMT.vgbx Gears[1..2].Ratio (Gear_1.vtlm, Gear_2.vtlm)
        i_adc=2.0,                        # BatteryElectricVehicle.vveh ElectricMotors[0].Ratio
        n_em=2,                           # BatteryElectricVehicle.vveh ElectricMotors[0].Count
        axle_map=read_vtlm(os.path.join(d, "Axle_4x2_Tractor.vtlm")),
        gear_maps=[read_vtlm(os.path.join(d, "Gear_1.vtlm")), read_vtlm(os.path.join(d, "Gear_2.vtlm"))],
        em_map=read_vemo(os.path.join(d, "GenericMap_125kW_485Nm.vemo")),
        em_limits=read_vemp(os.path.join(d, "GenericEMotor_125kW_485Nm.vemp")),
        rotor_inertia=0.225,              # GenericEMotor_125kW_485Nm.vem Inertia (per motor, kg m2)
        r_dyn=0.4209,                     # BEV_E2.vsum 'r_dyn [m]'
    )


def run_e2_drivetrain(e2, P_wheel, w_wheel, gear, P_rot, P_pto=0.0, eta_adc=1.0, **kw):
    """Call the verbatim `drivetrain` with the E2 inputs."""
    return drivetrain(P_wheel, w_wheel, gear, e2["i_axle"], e2["axle_map"], e2["i_gears"], e2["gear_maps"],
                      e2["i_adc"], eta_adc, e2["n_em"], e2["em_map"], e2["em_limits"][0], e2["em_limits"][1],
                      P_rot, P_pto)


def vecto_loss_map(table):
    """READER (not a change to `drivetrain`): convert a VECTO loss map (input speed, INPUT torque, loss) into the
    coordinates VECTO actually triangulates on: (input speed, input torque - loss) = output torque in input units.
    [VECTO] VectoCore/VectoCore/Models/SimulationComponent/Data/Gearbox/TransmissionLossMap.cs lines 76-77
    (AddPoint(InputSpeed, InputTorque - TorqueLoss, TorqueLoss)) and line 94 (lookup at out-speed*ratio,
    outTorque/ratio). Effect on E2 .vmod rows (gate_drivetrain.py): gearbox loss -2.1..-3.3 % -> within 0.06 %
    on non-shift rows."""
    b = np.array(table, dtype=float)
    b[:, 1] = b[:, 1] - b[:, 2]
    return b
