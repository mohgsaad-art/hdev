"""Method C fitted with VECTO in the loop (Part 2).

Same objective as PR #37 (methods_lib.fit_v2): least_squares on the relative residuals pred/cert - 1, bounds as PR #37 (eta_d 0.5-1, eta_r 0.3-1,
F0 0-3000 N, declared CdxA inside its Reg. 2018/956 range, measured air drag only), variables scaled by their upper bound, method 'trf'.
Every function value is one VECTO job (all certified results of the truck are produced by the same job, so hiding a result costs nothing extra);
every job is cached by parameter set (engines.vecto_run). The Jacobian is
  fd    forward differences, one VECTO job per parameter, run in parallel threads (the number of jobs = number of parameters), at every iteration
  broyden  forward differences at the start, then rank-one (Broyden) updates from the exact VECTO residuals of the accepted steps (1 job per iteration)
  fixed a Jacobian taken from a finite-difference evaluation at the full-data solution, rows of the used results only, kept constant
        (hide-one folds; the residuals are always exact VECTO values; convergence is verified by a final finite-difference gradient check)
"""
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from scipy.optimize import least_squares

import engines as E

WORKERS = int(os.environ.get("VECTO_WORKERS", "6"))
EPS_B = 1e-6


class Problem:
    def __init__(self, cid, f0_mode="axle", used=None, log=None):
        E.prewarm()
        self.cid, self.f0_mode = cid, f0_mode
        self.cert = E.certified(cid)
        self.n = len(self.cert)
        self.used = np.arange(self.n) if used is None else np.array(used)
        self.lo, self.hi, self.names = E.bounds(cid)
        self.scale = np.where(self.hi > 0, self.hi, 1.0)
        self.k = len(self.names)
        self.nfun = 0
        self.log = log or (lambda *a: None)
        self._lock = threading.Lock()
        self.pool = ThreadPoolExecutor(WORKERS)

    # ---- evaluation (cached on disk by parameter set)
    def vecto(self, theta):
        theta = np.clip(np.asarray(theta, float), self.lo, self.hi)
        r = E.vecto_run(self.cid, tuple(theta), self.f0_mode)
        return r["term"]

    def resid_all(self, theta):
        return self.vecto(theta) / self.cert - 1.0

    def fun_z(self, z):
        with self._lock:
            self.nfun += 1
        th = z * self.scale
        r = self.resid_all(th)[self.used]
        self.log("  f(%s) cost %.6g  [%.1f s]" % (np.round(th, 5), 0.5 * float(r @ r), time.time()))
        return r

    def fd_jac_all(self, theta, rel_step=1e-2):
        """d(residual)/d(theta) for ALL results, forward differences, one VECTO job per parameter (parallel)."""
        theta = np.clip(np.asarray(theta, float), self.lo, self.hi)
        base = self.resid_all(theta)
        thetas, hs = [], []
        for j in range(self.k):
            h = rel_step * self.scale[j]
            t = theta.copy()
            if theta[j] + h > self.hi[j]:
                h = -h
            t[j] += h
            thetas.append(t); hs.append(h)
        res = list(self.pool.map(self.resid_all, thetas))
        J = np.column_stack([(r - base) / h for r, h in zip(res, hs)])
        return J, base

    def jac_z_fd(self, z):
        J, _ = self.fd_jac_all(z * self.scale)
        return (J * self.scale)[self.used]

    # ---- fit
    def fit(self, theta0, jac="fd", J_all=None, max_nfev=12):
        z0 = np.clip(np.asarray(theta0, float), self.lo + EPS_B * (self.hi - self.lo), self.hi - EPS_B * (self.hi - self.lo)) / self.scale
        if jac == "fd":
            jf = self.jac_z_fd
        elif jac == "broyden":
            st = {}

            def jf(z):
                r = self.resid_all(z * self.scale)[self.used]
                if "J" not in st:
                    st["J"] = self.jac_z_fd(z)
                else:
                    dz = z - st["z"]
                    if np.linalg.norm(dz) > 1e-12:
                        st["J"] = st["J"] + np.outer((r - st["r"]) - st["J"] @ dz, dz) / float(dz @ dz)
                st["z"], st["r"] = z.copy(), r.copy()
                return st["J"]
        else:
            Jz = (J_all * self.scale)[self.used]
            jf = lambda z: Jz
        sol = least_squares(self.fun_z, z0, jac=jf, bounds=(self.lo / self.scale, self.hi / self.scale), method="trf", xtol=1e-4, ftol=1e-5,
                            gtol=1e-9, max_nfev=max_nfev)
        th = sol.x * self.scale
        r_all = self.resid_all(th)
        return dict(theta=th, resid_used=r_all[self.used], resid_all=r_all, cost=float(sol.cost), nfev=int(sol.nfev), status=int(sol.status), message=sol.message,
                    at_bound=[n for n, v, a, b in zip(self.names, th, self.lo, self.hi) if min(abs(v - a), abs(b - v)) <= 1e-3 * (b - a)])


def grad_check(P, theta, used):
    """Projected gradient of the used-residual cost at theta, from a fresh finite-difference Jacobian (not the one used in the fit)."""
    J, base = P.fd_jac_all(theta)
    Ju, ru = J[used], base[used]
    g = (Ju.T @ ru) * P.scale
    free = np.array([not ((theta[j] <= P.lo[j] + 1e-3 * (P.hi[j] - P.lo[j]) and g[j] > 0) or (theta[j] >= P.hi[j] - 1e-3 * (P.hi[j] - P.lo[j]) and g[j] < 0))
                     for j in range(P.k)])
    return float(np.linalg.norm(g[free])) if free.any() else 0.0, J
