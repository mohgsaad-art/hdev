# STATUS: CURRENT (canonical driver model, post-14 April rewrite). Pasted by Bob 12 Oct 2026.
# PIPELINE STEP: G (driver model). AUDITED Step 9 item 4 (see docs/decisions/2026-10-08_session-closeout-payload-force.md section 6).
# NOTE: rows are list of dicts (time, distance, speed, accel, grade, payload, dt_s).
# NOTE: needs a Waypoint/vacc structure (src.resolver.waypoint_parser) - not standalone.
#
# ===========================================================================
# AUDIT (Step 9 item 4) - the class was NOT rewritten wholesale. Only clearly-correct,
# NON-GRADE fixes were applied, each listed below. The grade handling is 🔒 M0.12 and is
# left EXACTLY as it was (see "GRADE HANDLING" below).
#
# FIXES APPLIED (compared against src/deprecated/simulate_driver_alt.py and section 6 of the
# payload-force close-out):
#   F1. braking-distance div/0 guard (known bug #3, orange): in get_breaking_distance, a
#       non-negative deceleration lookup used to divide by abs(0) -> inf. Now a dec >= 0 is
#       clamped to a small negative (-0.01), mirroring the deprecated variant's guard.
#   F2. vacc_lookup None return (known bug #4, orange): the for-loop could fall through and
#       return None (then unpack-crash). Added an explicit fallback to the last curve point,
#       mirroring the deprecated variant.
#   F3. standstill-start safety (part of known bug #1, red - infinite-loop risk): when the
#       truck is at ~0 speed with a positive cruise target but the clamped accel is <= 0, it
#       could never pull away and the while-loop would spin forever. Now acc = max_acc in that
#       case (deprecated variant's "Safety for start from standstill").
#   F4. snap-to-stop / no-progress guard (part of known bug #1, red): when ds and the new speed
#       are both ~0 and the target speed is 0, snap exactly to the stop waypoint and break,
#       instead of looping with no distance progress (deprecated variant's "Prevent numerical
#       lo0k-up"). This closes the remaining infinite-loop path near a stop.
#   F5. payload column (audit item, close-out section 2): every emitted row now carries a
#       'payload' field, copied exactly like grade (driving rows current.payload, stopped rows
#       target.payload, first-waypoint stop loop waypoints[0].payload). payload is read with a
#       getattr fallback of 0.0 so fill_payload is optional and old waypoints still work.
#
# THE 6 KNOWN BUGS (close-out section 6; status after this audit):
#   #1 (red)    infinite-loop risk near a stop / standstill start   -> MITIGATED by F3 + F4.
#   #2 (red)    segment-level vs step-level acceleration (cruise_speed is chosen per step from
#               the waypoint, not a segment-level plan) -> NOT fixed here (needs a design call on
#               the acceleration strategy; not a clearly-correct local fix). Left as-is, flagged.
#   #3 (orange) div/0 in braking distance                           -> FIXED by F1.
#   #4 (orange) vacc_lookup can return None                         -> FIXED by F2.
#   #5 (yellow) on arrival speed is set to target_speed directly and the overshoot ds is dropped
#               (a speed jump without a matching accel row) -> NOT changed: it matches VECTO's
#               snap-to-waypoint and changing it would alter the force/energy trace. Flagged.
#   #6 (yellow) unclamped accel is stored on a row even when new_speed is clamped to 0; the force
#               engine already compensates by clamping v2 at 0 (close-out section 4) -> left as-is
#               by design so the two engines stay consistent. Flagged.
#
# GRADE HANDLING - 🔒 M0.12 - LEFT EXACTLY AS IS:
#   This model copies the FLAT grade_pct straight from the waypoint onto each per-second row
#   (driving rows current.grade_pct, stopped rows target.grade_pct). VECTO instead derives the
#   per-step inclination from an ALTITUDE secant between waypoints (the deprecated variant even
#   interpolates grade, which is still NOT the VECTO altitude method). Picking the correct grade
#   model is locked as M0.12 and is Bob's call, so NOTHING about grade was changed here.
# ===========================================================================

#driver model -> taked vdri waypoints and vacc files and outputs speed trace events with coasting, cruising and breaking

class DriverModel:
    def __init__(self, waypoints):
        self.waypoints = waypoints

    def get_breaking_distance(self, v0,v1, vacc): # takes in waypoint speed and next waypoint speed calcs breaking distance
      breakpoints = [v1]
      for pt in vacc:
          v_ms = pt.speed / 3.6
          if v1 < v_ms < v0:
              breakpoints.append(v_ms)
      breakpoints.append(v0)
      breakpoints.sort()

      breaking_ds = 0.0
      for i in range(len(breakpoints)-1):
        if v1 <= breakpoints[i] <= v0:
          v_mid = (breakpoints[i] + breakpoints[i+1]) / 2
          dec_at_vmid = self.vacc_lookup(v_mid,vacc)[1]
          if dec_at_vmid >= 0:    # F1: guard div/0 - a non-negative dec would blow up abs(0) (known bug #3)
            dec_at_vmid = -0.01
          breaking_ds += (breakpoints[i+1] ** 2 - breakpoints[i] ** 2) / (2 * abs(dec_at_vmid))
      return breaking_ds


    def vacc_lookup(self,v, vacc): # takes in speed and gives out acc and dec

        v_kmh = v * 3.6
        if v_kmh <= vacc[0].speed:
            return vacc[0].acc, vacc[0].dec
        if v_kmh >= vacc[-1].speed:
            return vacc[-1].acc, vacc[-1].dec
        for i in range(len(vacc) - 1):
            if vacc[i].speed <= v_kmh <= vacc[i+1].speed:
                t = (v_kmh - vacc[i].speed) / (vacc[i+1].speed - vacc[i].speed)
                acc = vacc[i].acc + t * (vacc[i+1].acc - vacc[i].acc)
                dec = vacc[i].dec + t * (vacc[i+1].dec - vacc[i].dec)
                return acc, dec
        return vacc[-1].acc, vacc[-1].dec   # F2: never fall through to None (known bug #4)


    def driver_model(self, vacc, dt_s = 1.0):

      rows = []
      time= 0.0
      distance= self.waypoints[0].distance
      speed= self.waypoints[0].speed / 3.6 #kmh to m/s

      if self.waypoints[0].stop > 0.0:# this is exclusively for 1st waypoint
        t_elapsed = 0.0
        while t_elapsed < self.waypoints[0].stop:
          rows.append({
            'time':     time,
            'distance': distance,
            'speed':    0.0,
            'accel':    0.0,
            'grade':    self.waypoints[0].grade_pct,
            'payload':  getattr(self.waypoints[0], 'payload', 0.0),  # F5: copy payload like grade
            'dt_s':     dt_s })
          time      += dt_s
          t_elapsed += dt_s
        speed = 0.0

      for i in range(len(self.waypoints) - 1):
        current= self.waypoints[i]
        target= self.waypoints[i+1]
        target_speed = target.speed / 3.6
        target_distance = target.distance

        while distance < target_distance: #this is if v1 <= v0

          breaking_ds = self.get_breaking_distance(speed, target_speed, vacc) #breaking distance
          breaking_ds_start = target_distance - breaking_ds

          if distance >= breaking_ds_start: #breaking phase
            cruise_speed = target_speed

          else:                               ###crusing / accelerate
            cruise_speed = max(current.speed / 3.6, target_speed)

          max_acc, max_dec = self.vacc_lookup(speed, vacc)

          remaining_distance = target_distance - distance

          if (speed + cruise_speed) > 0 and remaining_distance > 0:
            dt_required = 2 * remaining_distance / (speed + cruise_speed)
            acc_required = (cruise_speed - speed) / dt_required

          else:
            acc_required = 0.0

          acc = max(max_dec, min(max_acc, acc_required))

          # F3: safety for a start from standstill - if stuck at ~0 speed with a positive
          # cruise target but a non-positive clamped accel, the loop would never move. Pull away.
          if speed <= 1e-9 and cruise_speed > 0 and acc <= 0:
            acc = max_acc

          new_speed = max (0.0, speed + acc * dt_s)
          ds = speed * dt_s + 0.5 * acc * dt_s **2
          ds = max(0.0, ds)

          # F4: no-progress snap guard - if neither distance nor speed advances and the target
          # is a stop, snap exactly to the stop waypoint instead of looping forever (bug #1).
          if ds <= 1e-9 and new_speed <= 1e-9 and target_speed == 0.0:
            rows.append({
            'time':     time,
            'distance': distance,
            'speed':    speed ,
            'accel':    acc,
            'grade':    current.grade_pct,
            'payload':  getattr(current, 'payload', 0.0),  # F5
            'dt_s':     dt_s })
            distance = target_distance
            speed = target_speed
            time += dt_s
            break

          if distance + ds >= target_distance:
            rows.append({
            'time':     time,
            'distance': distance,
            'speed':    speed ,
            'accel':    acc,
            'grade':    current.grade_pct,
            'payload':  getattr(current, 'payload', 0.0),  # F5: copy payload like grade
            'dt_s':     dt_s })

            distance = target_distance
            speed = target_speed
            time += dt_s
            break

          rows.append({
            'time':     time,
            'distance': distance,
            'speed':    speed ,
            'accel':    acc,
            'grade':    current.grade_pct,
            'payload':  getattr(current, 'payload', 0.0),  # F5: copy payload like grade
            'dt_s':     dt_s })
          distance += ds
          speed = new_speed
          time += dt_s

        if target.stop > 0.0:
          speed = 0.0
          t_elapsed = 0.0

          while t_elapsed < target.stop:

            rows.append({
                'time':     time,
                'distance': distance,
                'speed':    0.0,
                'accel':    0.0,
                'grade':    target.grade_pct,
                'payload':  getattr(target, 'payload', 0.0),  # F5: copy payload like grade
                'dt_s':     dt_s })
            time      += dt_s
            t_elapsed += dt_s

      return rows
