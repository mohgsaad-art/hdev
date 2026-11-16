"""Calibration methods A, C, L1, L2, L3, G (Part B) and the leave-one-out machinery (Part C).

The physics (driver, force engine, tyres, aux, crosswind, rho 1.188) comes from the v2 harness
through harness.py: every run gives P_wheel (zero drivetrain drag), P_aux, M, V, v_avg, km.
Only the step that turns wheel power into battery power differs between methods. That step is
a copy of consumption_engine lines 529-533 (Bob's notebook, via v2 hdev_test_module) with the
efficiency allowed to be a number or a curve of the load fraction. The copy is checked against
the real consumption_engine in tests (method A must equal the v2 V-A result).
"""
import numpy as np
from scipy.optimize import least_squares

CHARGING_ETA = 0.995                  # job prompt s.2: certified kWh/km is grid-side, energy / 0.995
V_NO_REGEN = 5.0 / 3.6                # v2 harness / notebook v_min_coast / 3 Nov matrix
# method A constants = v2 _drivetrains.VA_* (3 Nov matrix values)
A_MOTOR, A_INV, A_GBX, A_REGEN = 0.95, 0.95, 0.98, 0.95
# 7 Nov bounds (job prompt Part B): keep unless a reason is shown
BND_ETA = (0.5, 1.0)
BND_REGEN = (0.3, 1.0)
BND_F0 = (0.0, 3000.0)
BND_CDXA = (3.0, 11.0)


class Shape:
    """Efficiency shape from Part A (partA_shapes.csv). Stored as LOSS FACTORS, so a scale factor stretches the
    losses, not the efficiency:
        driving    k_d(x) = 1/eta_d(x) - 1     (electric loss per kWh at the wheel)   P_el = P_w * (1 + s_d * k_d(x))
        recovering l_r(x) = 1 - eta_r(x)       (share of wheel energy lost)            P_el = P_w * (1 - s_r * l_r(x))
    x = |P_wheel| / P_rated. Piecewise linear between bin centres (energy-weighted x), flat outside.
    eta_bar_d / eta_bar_r: energy-weighted chain efficiency of the shape over all its Part A runs; used for the
    scale bounds (see scale_bounds)."""

    def __init__(self, name, x_d, eta_d, x_r, eta_r, eta_bar_d, eta_bar_r):
        self.name = name
        self.x_d, self.k_d = np.asarray(x_d, float), 1.0 / np.asarray(eta_d, float) - 1.0
        self.x_r, self.l_r = np.asarray(x_r, float), 1.0 - np.asarray(eta_r, float)
        self.eta_bar_d, self.eta_bar_r = float(eta_bar_d), float(eta_bar_r)

    def kd(self, x):
        return np.interp(x, self.x_d, self.k_d)

    def lr(self, x):
        return np.interp(x, self.x_r, self.l_r)

    def scale_bounds(self):
        """Scale bounds tied to the 7 Nov efficiency bounds. A scale s turns the shape's mean efficiency eta_bar into
        eta' with 1/eta' - 1 = s (1/eta_bar - 1) (driving) and 1 - eta' = s (1 - eta_bar) (recovering).
        s = 0 gives eta' = 1.0 (7 Nov upper bound). s_max gives eta' = 0.5 driving / 0.3 recovering (7 Nov lower bounds)."""
        sd = (1.0 / BND_ETA[0] - 1.0) / (1.0 / self.eta_bar_d - 1.0)
        sr = (1.0 - BND_REGEN[0]) / (1.0 - self.eta_bar_r)
        return sd, sr


def load_shapes(path=None):
    """Read partA_shapes.csv + partA_shape_summary.csv -> {name: Shape}."""
    import csv
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    path = path or os.path.join(here, "partA_shapes.csv")
    rows = list(csv.DictReader(open(path)))
    summ = list(csv.DictReader(open(os.path.join(os.path.dirname(path), "partA_shape_summary.csv"))))
    out = {}
    for name in sorted(set(r["shape"] for r in rows)):
        d = sorted([r for r in rows if r["shape"] == name and r["side"] == "drive"], key=lambda r: float(r["x_mid"]))
        g = sorted([r for r in rows if r["shape"] == name and r["side"] == "regen"], key=lambda r: float(r["x_mid"]))
        su = [r for r in summ if r["shape"] == name]
        wd = sum(float(r["wheel_drive_kwh_km"]) for r in su)
        ed = sum(float(r["wheel_drive_kwh_km"]) / float(r["eta_drive"]) for r in su)
        wr = sum(float(r["wheel_regen_kwh_km"]) for r in su)
        er = sum(float(r["wheel_regen_kwh_km"]) * float(r["eta_regen"]) for r in su)
        out[name] = Shape(name, [float(r["x_mid"]) for r in d], [float(r["eta"]) for r in d],
                          [float(r["x_mid"]) for r in g], [float(r["eta"]) for r in g], wd / ed, er / wr)
    return out


# default shape per architecture (Part A5; Kiro's choice, changes the least: the VECTO example that has the
# same layout as the truck)
ARCH_SHAPE = {"E2": "S1_E2", "E3": "S1_E2", "E4": "S1_E2",
              "E-IEPC:1": "S3a_IEPC_1speed", "E-IEPC:n": "S3b_IEPC_3speed", "E-IEPC-wheel": "S3c_IEPC_wheel_1speed"}


def arch_key(rec):
    a = rec["arch"]
    if a == "E-IEPC":
        return "E-IEPC:1" if (rec.get("n_gears") or 1) <= 1 else "E-IEPC:n"
    return a


def traction_power(rec, eta_d=None, eta_r=None, F0=0.0, p_const=0.0, shape=None, s_d=1.0, s_r=1.0):
    """Copy of consumption_engine lines 529-533 (Bob's notebook via v2 hdev_test_module) with two extensions:
      * scalar efficiencies (eta_d, eta_r) exactly as consumption_engine, OR a shape (loss factors vs x, scaled);
      * F0 [N] drag force at the wheel (method C), p_const [W] constant loss while engaged (method L3)."""
    Pw = rec["P_wheel"] + F0 * rec["v_avg"]
    if shape is None:
        P = np.where(Pw > 0, Pw / eta_d, Pw * eta_r)
    else:
        x = np.abs(Pw) / (rec["rated_kw"] * 1000.0)
        P = np.where(Pw > 0, Pw * (1.0 + s_d * shape.kd(x)), Pw * (1.0 - s_r * shape.lr(x)))
    # consumption_engine 531-532 (M == 3 -> 0; M == 4 and V <= v_no_regen -> 0): those rows were removed
    # when the record was compacted (harness.compact), so every row here is a row where traction applies.
    if p_const:
        P = P + np.where(rec["engaged"], p_const, 0.0)
    return P


def kwh_per_km(rec, P_trac):
    E = (np.sum(P_trac) + rec["E_aux_Ws"]) / 3.6e6     # dt = 1 s per row (v2 harness)
    return E / rec["km"] / CHARGING_ETA


class Method:
    name = "?"
    needs_rated = False
    path = ""
    names = ()

    def predict(self, rec, theta):
        raise NotImplementedError


class MethodA(Method):
    name = "A"
    names = ()
    bounds = ((), ())
    starts = [()]
    path = "sizing and per-truck (no inputs needed)"

    def predict(self, rec, theta=()):
        return kwh_per_km(rec, traction_power(rec, A_MOTOR * A_INV * A_GBX, A_REGEN))


class MethodC(Method):
    name = "C"
    names = ("eta", "regen", "F0")
    bounds = ((BND_ETA[0], BND_REGEN[0], BND_F0[0]), (BND_ETA[1], BND_REGEN[1], BND_F0[1]))
    starts = [(0.9, 0.8, 300.0), (0.7, 0.6, 1000.0), (0.95, 0.95, 0.0)]
    path = "per-truck only (needs that truck's certified results)"

    def predict(self, rec, theta):
        eta, reg, F0 = theta
        return kwh_per_km(rec, traction_power(rec, eta, reg, F0=F0))


class _ShapeMethod(Method):
    needs_rated = True
    path = "per-truck (needs EEA rated power + that truck's certified results)"

    def __init__(self, shapes, fixed_shape=None):
        self.shapes = shapes
        self.fixed_shape = fixed_shape
        self.tag = fixed_shape or "arch"

    def shape_for(self, rec):
        return self.shapes[self.fixed_shape or ARCH_SHAPE[arch_key(rec)]]

    def bounds_for(self, rec):
        raise NotImplementedError


class MethodL1(_ShapeMethod):
    """P_el = P_w (1 + s k_d(x)) driving, P_w (1 - s l_r(x)) recovering. One fitted s (+CdxA)."""
    names = ("s",)
    starts = [(1.0,), (0.5,), (1.5,)]

    def __init__(self, shapes, fixed_shape=None):
        super().__init__(shapes, fixed_shape)
        self.name = "L1[%s]" % self.tag

    def bounds_for(self, rec):
        sd, sr = self.shape_for(rec).scale_bounds()
        return (0.0,), (min(sd, sr),)

    def predict(self, rec, theta):
        return kwh_per_km(rec, traction_power(rec, shape=self.shape_for(rec), s_d=theta[0], s_r=theta[0]))


class MethodL2(_ShapeMethod):
    names = ("s_drive", "s_regen")
    starts = [(1.0, 1.0), (0.5, 0.5), (1.5, 1.5)]

    def __init__(self, shapes, fixed_shape=None):
        super().__init__(shapes, fixed_shape)
        self.name = "L2[%s]" % self.tag

    def bounds_for(self, rec):
        sd, sr = self.shape_for(rec).scale_bounds()
        return (0.0, 0.0), (sd, sr)

    def predict(self, rec, theta):
        return kwh_per_km(rec, traction_power(rec, shape=self.shape_for(rec), s_d=theta[0], s_r=theta[1]))


# L3 constant-loss upper bound = largest no-load electric power / P_rated seen in any VECTO shape at any cycle
# speed (partA_no_load_loss.csv, column max). Read at run time by the scripts (set_c_max).
C_MAX = None


def set_c_max(value):
    global C_MAX
    C_MAX = float(value)


class MethodL3(_ShapeMethod):
    """L1 + constant loss power c * P_rated on every engaged row (the 'sourced form' is VECTO's own no-load loss:
    loss maps have a torque loss at zero torque that grows with speed; c lumps it into one constant)."""
    names = ("s", "c")
    starts = [(1.0, 0.0), (0.5, 0.01), (1.5, 0.0)]

    def __init__(self, shapes, fixed_shape=None):
        super().__init__(shapes, fixed_shape)
        self.name = "L3[%s]" % self.tag

    def bounds_for(self, rec):
        sd, sr = self.shape_for(rec).scale_bounds()
        return (0.0, 0.0), (min(sd, sr), C_MAX)

    def predict(self, rec, theta):
        s, c = theta
        return kwh_per_km(rec, traction_power(rec, shape=self.shape_for(rec), s_d=s, s_r=s,
                                              p_const=c * rec["rated_kw"] * 1000.0))


class MethodL1F(_ShapeMethod):
    """Kiro's extra variant (not in the job table): L1 shape x s PLUS method C's drag force F0 at the wheel.
    Tests the shape against C's constant efficiencies with the same F0 term (a fair head-to-head)."""
    names = ("s", "F0")
    starts = [(1.0, 300.0), (0.5, 1000.0), (1.5, 0.0)]

    def __init__(self, shapes, fixed_shape=None):
        super().__init__(shapes, fixed_shape)
        self.name = "L1F[%s]" % self.tag

    def bounds_for(self, rec):
        sd, sr = self.shape_for(rec).scale_bounds()
        return (0.0, BND_F0[0]), (min(sd, sr), BND_F0[1])

    def predict(self, rec, theta):
        s, F0 = theta
        return kwh_per_km(rec, traction_power(rec, shape=self.shape_for(rec), s_d=s, s_r=s, F0=F0))


class MethodG(_ShapeMethod):
    """Sizing path: class curve = shape + class-median fitted scale values (no per-truck fit). theta is the class value."""
    path = "sizing (needs only class, architecture, EEA-type rated power)"

    def __init__(self, shapes, base_method, theta, fixed_shape=None):
        super().__init__(shapes, fixed_shape)
        self.base = base_method
        self.theta = tuple(theta)
        self.name = "G[%s]" % base_method.name
        self.names = ()

    def predict(self, rec, theta=()):
        return self.base.predict(rec, self.theta)


class WithCdxA(Method):
    """Adds one fitted effective CdxA0 [m2] (bounds 3-11, 7 Nov) to any method. P_wheel is linear in CdxA0
    (aero_k = rho * L * W1(v), harness.py). Used only where EEA says the air drag was MEASURED
    (the standard value is what VECTO itself used otherwise). The fitted value is an EFFECTIVE value."""

    def __init__(self, base, start_scale=(1.0, 0.8, 1.2)):
        self.base = base
        self.name = base.name + "+CdxA"
        self.names = tuple(base.names) + ("cdxa",)
        self.needs_rated = base.needs_rated
        self.path = base.path
        self._start_scale = start_scale
        self.starts = None

    def bounds_for(self, rec):
        lo, hi = self.base.bounds_for(rec) if hasattr(self.base, "bounds_for") else self.base.bounds
        return tuple(lo) + (BND_CDXA[0],), tuple(hi) + (BND_CDXA[1],)

    def _starts_for(self, rec):
        return [tuple(b) + (float(np.clip(rec["cdxa0"] * k, *BND_CDXA)),)
                for b, k in zip(self.base.starts * len(self._start_scale), np.repeat(self._start_scale, len(self.base.starts)))]

    def predict(self, rec, theta):
        r2 = dict(rec)
        r2["P_wheel"] = rec["P_wheel"] + rec["aero_k"] * (theta[-1] - rec["cdxa0"])
        return self.base.predict(r2, tuple(theta[:-1]))


# ------------------------------------------------------------------------------------------
# fitting
# ------------------------------------------------------------------------------------------
def fit(method, recs):
    """Least squares on relative error (pred - cert) / cert with bounds; deterministic multi-start
    (fixed start list, no random numbers). Returns (theta, rms_rel_error)."""
    if len(method.names) == 0:
        return (), 0.0
    certs = np.array([r["cert"] for r in recs])

    def resid(th):
        return np.array([method.predict(r, th) for r in recs]) / certs - 1.0
    best = None
    lo, hi = method.bounds_for(recs[0]) if hasattr(method, "bounds_for") else method.bounds
    lo, hi = np.array(lo, float), np.array(hi, float)
    starts = method._starts_for(recs[0]) if isinstance(method, WithCdxA) else method.starts
    for x0 in starts:
        x0 = np.clip(np.array(x0, float), lo, hi - 1e-12 * np.maximum(1.0, np.abs(hi)))
        sol = least_squares(resid, x0, bounds=(lo, hi), method="trf", x_scale="jac",
                            xtol=1e-10, ftol=1e-10, gtol=1e-10, max_nfev=200)
        if best is None or sol.cost < best.cost - 1e-15:
            best = sol
    rms = float(np.sqrt(np.mean(best.fun ** 2)))
    return tuple(float(v) for v in best.x), rms


def loo(method, recs):
    """Leave-one-out over the certified results of one truck. Each result is predicted with a fit made
    without it. Returns list of dict (one per result) and the full-data fit."""
    out = []
    for i, r in enumerate(recs):
        train = [q for j, q in enumerate(recs) if j != i]
        if method.needs_rated and (r["rated_kw"] is None):
            out.append(dict(i=i, pred=np.nan, err=np.nan, blocked="no_rated_power"))
            continue
        th, _ = fit(method, train)
        p = method.predict(r, th)
        out.append(dict(i=i, pred=p, err=p / r["cert"] - 1.0, theta=th, blocked=""))
    return out


# ==========================================================================================================
# v2 job (16 Nov, prompt kiro-prompt-drivetrain-c-vs-equation-2026-11-16.md): L4 loss equations + CdxA in range
# ==========================================================================================================
# Upper bounds of the L4 coefficients, as fractions of the truck's rated power, derived from VECTO's generic maps
# by part2_methods.py (part2_L4_bounds.csv). Set at run time with set_l4_bounds().
L4_BOUNDS = {}


def set_l4_bounds(a_frac, b_frac, c_frac):
    """a_max = a_frac * P_rated [W]; b_max = b_frac / P_rated [1/W]; c_max = c_frac * P_rated [W per m/s]."""
    L4_BOUNDS.update(a=float(a_frac), b=float(b_frac), c=float(c_frac))


def l4_loss(rec, a, b, c=0.0, Pw=None):
    """P_loss = a + c*v + b*P^2 on every row where the drivetrain is engaged (rows already masked like
    consumption_engine: no M==3 coasting rows, no M==4 rows at V <= v_no_regen; 'engaged' = M != 0)."""
    Pw = rec["P_wheel"] if Pw is None else Pw
    return np.where(rec["engaged"], a + c * rec["v_avg"] + b * Pw * Pw, 0.0)


class MethodL4a(Method):
    """P_el = P_wheel + P_loss on engaged rows (driving: P + loss; recovering: |P_el| = |P| - loss),
    P_loss = a + b P^2.  a [W] ~ Annex Xb App.8 k_00 (constant loss); b [1/W] ~ k_20 (|T|^2, copper loss)
    referred to wheel power."""
    names = ("a_W", "b_perW")
    path = "per-truck (needs EEA rated power for the bounds + that truck's certified results)"
    needs_rated = True

    def __init__(self):
        self.name = "L4a"

    def _p(self, rec):
        return rec["rated_kw"] * 1000.0

    def bounds_for(self, rec):
        P = self._p(rec)
        return (0.0, 0.0), (L4_BOUNDS["a"] * P, L4_BOUNDS["b"] / P)

    def starts_for(self, rec):
        lo, hi = self.bounds_for(rec)
        return [tuple(h * f for h in hi) for f in (0.05, 0.2, 0.5)]

    def predict(self, rec, theta):
        a, b = theta
        P = rec["P_wheel"] + l4_loss(rec, a, b)
        return kwh_per_km(rec, P)


class MethodL4b(MethodL4a):
    """L4a + c*v: speed-only loss, standing for the k_0n |w|^n terms of Annex Xb App.8 (iron/friction/windage),
    with vehicle speed v as the proxy for motor speed (EEA has no gear ratios for multi-speed trucks)."""
    names = ("a_W", "b_perW", "c_W_per_mps")

    def __init__(self):
        self.name = "L4b"

    def bounds_for(self, rec):
        P = self._p(rec)
        return (0.0, 0.0, 0.0), (L4_BOUNDS["a"] * P, L4_BOUNDS["b"] / P, L4_BOUNDS["c"] * P)

    def predict(self, rec, theta):
        a, b, c = theta
        P = rec["P_wheel"] + l4_loss(rec, a, b, c)
        return kwh_per_km(rec, P)


class MethodCv2(MethodC):
    """Method C exactly as before (eta_d, eta_r, F0). Bounds: eta_d 0.5-1.0, eta_r 0.3-1.0, F0 0-3000 N
    [ASSUMPTION: job prompt values]."""

    def starts_for(self, rec):
        return [(0.9, 0.8, 300.0), (0.7, 0.6, 1000.0), (0.95, 0.95, 0.0)]


class WithCdxARange(Method):
    """Adds the DECLARED CdxA (data entry 23) as a fitted value, bounded to the truck's published range
    [min, max) of Reg. (EU) 2018/956 Annex I Part C. Only for trucks with MEASURED air drag. VECTO applies the
    declared value on every mission except Construction (AirdragDataAdapter.cs 147-149), so Construction runs do
    not move. P_wheel is linear in CdxA (aero_k = rho*L*W1(v)); checked against a full re-run in part1."""

    def __init__(self, base):
        self.base = base
        self.name = base.name + "+CdxA"
        self.names = tuple(base.names) + ("cdxa_declared",)
        self.needs_rated = getattr(base, "needs_rated", False)
        self.path = base.path

    @staticmethod
    def _range(rec):
        import harness as HN
        return HN.CDXA_RANGES[rec["cdxa_range"]]

    def bounds_for(self, rec):
        lo, hi = self.base.bounds_for(rec) if hasattr(self.base, "bounds_for") else self.base.bounds
        r = self._range(rec)
        return tuple(lo) + (r[0],), tuple(hi) + (r[1] - 1e-6,)          # max is exclusive (CdxA < max)

    def starts_for(self, rec):
        base = self.base.starts_for(rec) if hasattr(self.base, "starts_for") else self.base.starts
        r = self._range(rec)
        return [tuple(b) + (0.5 * (r[0] + r[1]),) for b in base]

    def predict(self, rec, theta):
        r2 = dict(rec)
        if rec["cdxa_hi"] > rec["cdxa_lo"]:                               # mission uses the declared value
            r = self._range(rec)
            r2["P_wheel"] = rec["P_wheel"] + rec["aero_k"] * (theta[-1] - 0.5 * (r[0] + r[1]))
        return self.base.predict(r2, tuple(theta[:-1]))


def fit_v2(method, recs):
    """least_squares on relative residuals, bounds as stated, 3 fixed starts, keep the best (no random numbers).
    Returns (theta, rms)."""
    if not method.names:
        return (), 0.0
    certs = np.array([r["cert"] for r in recs])
    lo, hi = method.bounds_for(recs[0])
    lo, hi = np.array(lo, float), np.array(hi, float)
    scale = np.where(hi > 0, hi, 1.0)

    def resid(z):
        th = z * scale
        return np.array([method.predict(r, th) for r in recs]) / certs - 1.0
    best = None
    for x0 in method.starts_for(recs[0]):
        z0 = np.clip(np.array(x0, float) / scale, lo / scale, hi / scale)
        sol = least_squares(resid, z0, bounds=(lo / scale, hi / scale), method="trf", xtol=1e-10, ftol=1e-10,
                            gtol=1e-10, max_nfev=300)
        if best is None or sol.cost < best.cost - 1e-15:
            best = sol
    return tuple(float(v) for v in best.x * scale), float(np.sqrt(np.mean(best.fun ** 2)))


def loo_v2(method, recs, groups=None):
    """Leave-one-out. groups=None: leave one RESULT out; else list of group labels (leave one GROUP out)."""
    labels = list(range(len(recs))) if groups is None else list(groups)
    out = [None] * len(recs)
    for g in dict.fromkeys(labels):
        train = [r for r, l in zip(recs, labels) if l != g]
        th, _ = fit_v2(method, train) if method.names else ((), 0.0)
        for i, (r, l) in enumerate(zip(recs, labels)):
            if l == g:
                p = method.predict(r, th)
                out[i] = dict(pred=p, err=p / r["cert"] - 1.0, theta=th)
    return out
