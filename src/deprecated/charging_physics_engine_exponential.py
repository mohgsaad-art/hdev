# STATUS: DEPRECATED - to be replaced. Pasted by Bob 12 Oct 2026 ("from old code").
# Decision (earlier sessions): replace the exponential CC-CV taper with the VECTO OCV + internal-resistance (Ri) approach,
# and split charger sizing into two functions: sizing mode (P = E/t, division-based minimum power) and
# simulation mode (per-timestep OCV+Ri loop). Not yet coded.
# Every constant below (SOC_THRESHOLD 0.90, K 1.0, ETA 0.95, V2G floor -0.2) is UNSOURCED and hard-coded,
# which breaks the "all parameters as arguments" rule.
import math

def charging_physics_engine(charge_rate_kw, battery_capacity_kwh,
                             current_capacity_kwh, charge_time_min,
                             v2g_flag, soc_floor=0.0):

    SOC_THRESHOLD = 0.90   # NMC CC-CV transition
    K             = 1.0    # exponential decay constant
    ETA           = 0.95   # charger efficiency

    SOC_FLOOR = -0.2 if v2g_flag else 0.0   # V2G allows drawing below normal floor
    SOC_CEIL  = 1.0

    charge_trace = []
    soc_trace    = []

    current_kwh = current_capacity_kwh

    for i in range(charge_time_min):
        soc = current_kwh / battery_capacity_kwh

        if soc >= SOC_CEIL:
            break

        if soc < SOC_THRESHOLD:
            p_delivered = charge_rate_kw * ETA                          # CC phase
        else:
            soc_norm    = (soc - SOC_THRESHOLD) / (1.0 - SOC_THRESHOLD)
            p_delivered = charge_rate_kw * ETA * math.exp(-K * soc_norm)  # CV phase

        kwh_this_min = p_delivered / 60
        current_kwh  = min(current_kwh + kwh_this_min,
                           SOC_CEIL * battery_capacity_kwh)

        charge_trace.append(p_delivered)
        soc_trace.append(current_kwh / battery_capacity_kwh)

    return soc_trace, current_kwh, charge_trace
