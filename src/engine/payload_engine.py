# STATUS: DONE and tested (step H). payload_engine pasted by Bob 12 Oct 2026.
# fill_payload is copied from docs/decisions/session-closeout-2026-10-08-payload-force.md (it was not in the 12 Oct paste;
# Bob to confirm it is still the current version in the notebook).
# Design: see docs/design/payload-stop-rows-then-fill.md
import numpy as np

##2 Payload engine
# pure logic, does not care if waypoints came from vdri, typed input or gps
# writes payload only on the start row and on stop rows, everything else stays blank (NaN)
# the blanks get filled forward later so ui can edit stop rows directly

def payload_engine(stop, shape, payload_start, payload_end=None, payload_custom=None): #stop duration column, starting payload

  stop = np.asarray(stop, dtype=float) # stop time of every waypoint/row in s, 0 means no stop; this is just the stop column from vecto or custom inputs

  is_stop = stop > 0 # true where the vehicle stops
  is_stop[0] = False # first row is the depot start, its dwell is not a payload change
  n_stops = int(is_stop.sum()) # number of stops where load can change

  # one payload for the start + one after each stop
  if shape == "constant":
      values = np.full(n_stops + 1, float(payload_start)) # same payload everywhere

  elif shape == "linear":
      if n_stops == 0:
          raise ValueError("linear needs at least one stop")
      values = np.linspace(payload_start, payload_end, n_stops + 1) # equal change at every stop, hdev assumption (unsourced)

  elif shape == "custom":
      values = np.asarray(payload_custom, dtype=float) # user gives start + one value per stop
      if len(values) != n_stops + 1:
          raise ValueError(f"custom needs {n_stops + 1} values, got {len(values)}")
  else:
      raise ValueError(f"unknown shape: {shape}")

  if np.any(values < 0):
      raise ValueError("payload cannot be negative")

  payload = np.full(len(stop), np.nan) # blank payload column, same length as waypoints
  payload[0] = values[0] # start payload always on row 0 so forward fill has something to start from
  payload[is_stop] = values[1:] # payload after each stop written on that stop row
  return payload


##3 Forward fill (runs just before the driver model)  -- from 8 Oct close-out
def fill_payload(payload):
  payload = np.asarray(payload, dtype=float)
  if np.isnan(payload[0]):
      raise ValueError("first row has no payload")
  idx = np.where(~np.isnan(payload), np.arange(len(payload)), 0)
  idx = np.maximum.accumulate(idx)
  return payload[idx]
