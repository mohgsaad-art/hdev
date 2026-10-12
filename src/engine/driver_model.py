# STATUS: CURRENT (canonical driver model, post-14 April rewrite). Pasted by Bob 12 Oct 2026.
# PIPELINE STEP: G (driver model). Under audit: 6 known bugs + extra items, see docs/decisions/2026-10-08_session-closeout-payload-force.md section 6.
# NOTE: rows are list of dicts (time, distance, speed, accel, grade, dt_s). Payload column not yet added (decided 8 Oct).
# NOTE: needs `import`s and a Waypoint/vacc structure from the notebook; not standalone.

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

          new_speed = max (0.0, speed + acc * dt_s)
          ds = speed * dt_s + 0.5 * acc * dt_s **2
          ds = max(0.0, ds)

          if distance + ds >= target_distance:
            rows.append({
            'time':     time,
            'distance': distance,
            'speed':    speed ,
            'accel':    acc,
            'grade':    current.grade_pct,
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
                'dt_s':     dt_s })
            time      += dt_s
            t_elapsed += dt_s

      return rows
