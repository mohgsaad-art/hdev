# STATUS: NOT WRITTEN (stub). Pasted by Bob 12 Oct 2026.
# The VECTO BEV lorry auxiliary logic is fully traced in docs/decisions/session-closeout-2026-10-08-paux.md:
#   P_aux(t) = P_ES + P_HVAC + P_PS + P_SP * [vehicle moving] + P_cond * [electric motor on]
# All five are electric, drawn from the traction battery, DC/DC efficiency = 1.0 in VECTO Declaration Mode.
# Design decisions still pending (Bob): default technologies, blank-cell handling, function structure, non-VECTO extras
# (cabin heating, DC/DC loss, aux during depot charging). Bob wants P_aux vehicle-agnostic (truck, van, bus, car).

##5 Paux
# must take in or read lookup tables and use waypoints to do the math for each of the 5 auxilary consumptions.
