# STATUS: NEW (Step 9 item 8 / M0.21, Bob to review). Pipeline step: battery power + energy.
# ROLE: turn per-row wheel power (power_step) + per-row aux power (p_aux) into per-row battery power
#   and an integrated energy figure in kWh.
#
# STRUCTURE (sign switch at P_wheel = 0):
#   P_wheel > 0  (traction, battery discharges) -> P_batt_trac = P_wheel / eta_drive
#   P_wheel <= 0 (braking, regen recharges)      -> P_batt_trac = P_wheel * eta_regen
#   then add the auxiliary draw through the DC/DC converter, and integrate Sigma * dt -> kWh.
#
# 🔒 EFFICIENCIES ARE HDEV PLACEHOLDERS (M0.21): eta_drive / eta_regen / eta_dcdc default to
#   0.95 / 0.95 / 0.98. These have NO VECTO EQUIVALENT (VECTO models a full drivetrain map, not a
#   single scalar efficiency). They are EXPLICIT ARGUMENTS so a caller can override them, and EVERY
#   result dict carries placeholder_efficiencies=True plus a message so the flag reaches the report.
#   The sign-switch + integration STRUCTURE is a reasonable, source-free placeholder structure (not a
#   VECTO formula). If Bob's notebook later provides an exact non-placeholder consumption formula, that
#   specific formula is what M0.21 locks - swap it in behind the same signature and drop the flag.
#
# PURITY (engine rules 1 + 7): every efficiency, P_aux and dt_s is an ARGUMENT; nothing is hard-coded
#   beyond the flagged placeholder DEFAULTS; no I/O. Vectorised over rows.
import numpy as np

# the message every result carries so the HDEV-placeholder nature reaches the client report.
PLACEHOLDER_MESSAGE = "contains HDEV placeholder efficiencies (no VECTO equivalent)"


def consumption(P_wheel, eta_drive=0.95, eta_regen=0.95, eta_dcdc=0.98, P_aux=0, dt_s=1.0):
  # per-row battery power [W] + integrated energy [kWh] from wheel power and auxiliaries.
  #   P_wheel   - per-row wheel power [W] (power_step)
  #   eta_drive - drive-path efficiency, battery -> wheel (HDEV placeholder, no VECTO equivalent)
  #   eta_regen - regen-path efficiency, wheel -> battery (HDEV placeholder, no VECTO equivalent)
  #   eta_dcdc  - DC/DC converter efficiency on the auxiliary draw (HDEV placeholder)
  #   P_aux     - per-row auxiliary electric power [W] (p_aux), scalar 0 if not modelled
  #   dt_s      - per-row time step [s]
  for name, val in (("eta_drive", eta_drive), ("eta_regen", eta_regen), ("eta_dcdc", eta_dcdc)):
    if val is None or val <= 0:
      raise ValueError("consumption: %s must be a positive efficiency, got %r" % (name, val))

  P_wheel = np.atleast_1d(np.asarray(P_wheel, dtype=float))
  P_aux = np.asarray(P_aux, dtype=float)
  dt_s = np.asarray(dt_s, dtype=float)

  # sign switch at P_wheel = 0 (traction divides by eta, regen multiplies by eta).
  traction = P_wheel > 0.0
  P_batt_trac = np.where(traction, P_wheel / eta_drive, P_wheel * eta_regen)

  # auxiliaries are drawn from the battery through the DC/DC converter (placeholder: divide by eta_dcdc).
  P_batt_aux = P_aux / eta_dcdc

  # per-row battery power [W]: positive = discharge, negative = net recharge from regen.
  P_batt = P_batt_trac + P_batt_aux

  # integrate: energy [J] = sum(P_batt * dt), then J -> kWh (/ 3.6e6).
  energy_J = float(np.sum(P_batt * dt_s))
  kWh = energy_J / 3.6e6

  return {
    "P_batt": P_batt,          # per-row battery power [W]
    "kWh": kWh,                # integrated battery energy over the trace [kWh]
    "placeholder_efficiencies": True,   # 🔒 M0.21 - always flagged
    "message": PLACEHOLDER_MESSAGE,
    "efficiencies": {"eta_drive": eta_drive, "eta_regen": eta_regen, "eta_dcdc": eta_dcdc},
  }
