"""Part 2: methods L1 and L1b built on the PR #37 shape library (partA_shapes.csv, re-run and identical, see README in the report).

  L1   drive losses = shape x s, regen losses = same shape x the same s        (one scale s)         ML.MethodL1
       P_el = P_w (1 + s k_d(x)) driving,  P_w (1 - s l_r(x)) recovering,  k_d = 1/eta_d(x) - 1,  l_r = 1 - eta_r(x),  x = |P_w| / P_rated
  L1b  separate scales s_drive, s_regen on the same shape                       (two scales)          ML.MethodL2
  both + the declared CdxA inside its Reg. 2018/956 range for measured air drag (ML.WithCdxARange), exactly like C and L4b.

Shape choice (ASSUMPTION): either one fixed shape for every truck, or the a-priori rule "arch" of PR #37 (ML.ARCH_SHAPE: E-IEPC with
one gear -> S3a_IEPC_1speed, E-IEPC with more gears -> S3b_IEPC_3speed, wheel-motor IEPC -> S3c_IEPC_wheel_1speed). The rule uses EEA attributes,
never the error of a truck. Scale bounds: ML.Shape.scale_bounds (s = 0 gives eta = 1.0; s_max gives eta_d 0.5 / eta_r 0.3, the 7 Nov bounds).
"""
import numpy as np

import lib_g5 as L

ML = L.ML
_SHAPES = None


def shapes():
    global _SHAPES
    if _SHAPES is None:
        _SHAPES = ML.load_shapes()
    return _SHAPES


class ShapeL1(ML.MethodL1):
    def starts_for(self, rec):
        return list(self.starts)


class ShapeL1b(ML.MethodL2):
    """L1b: separate drive and regen scales."""

    def __init__(self, shapes_, fixed_shape=None):
        super().__init__(shapes_, fixed_shape)
        self.name = "L1b[%s]" % self.tag

    def starts_for(self, rec):
        return list(self.starts)


def make(kind, shape_key, rec):
    """kind 'L1' or 'L1b'; shape_key 'arch' or a shape name."""
    fixed = None if shape_key == "arch" else shape_key
    base = (ShapeL1 if kind == "L1" else ShapeL1b)(shapes(), fixed)
    return ML.WithCdxARange(base) if rec["airdrag_measured"] else base


def label(kind, shape_key):
    return "%s[%s]" % (kind, shape_key)
