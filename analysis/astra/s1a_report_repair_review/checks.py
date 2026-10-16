"""Exact stopped-Bernoulli arithmetic and tiny collector fixtures; no simulations."""
import ast
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path

import numpy as np
import scipy
from scipy.stats import beta, binom, nbinom

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "analysis/fable/calibration/v2_dev/p2_stage1a.py"


def curtailed_check(c, m):
    t = np.arange(c, m + 1)
    h = np.arange(c)
    lo = np.r_[beta.ppf(.025, c, t-c+1), np.where(h > 0, beta.ppf(.025, h, m-h+1), 0)]
    hi = np.r_[np.where(t > c, beta.ppf(.975, c, t-c), 1), beta.ppf(.975, h+1, m-h)]
    p = np.arange(1, 1000) / 1000
    mass = np.c_[nbinom.pmf(t[None, :]-c, c, p[:, None]),
                 binom.pmf(h[None, :], m, p[:, None])]
    assert np.max(abs(mass.sum(axis=1)-1)) < 1e-12
    coverage = (mass*((p[:, None] >= lo) & (p[:, None] <= hi))).sum(axis=1)
    lower_error = (mass*(p[:, None] < lo)).sum(axis=1)
    upper_error = (mass*(p[:, None] > hi)).sum(axis=1)
    assert coverage.min() >= .95-1e-12
    assert lower_error.max() <= .025+1e-12 and upper_error.max() <= .025+1e-12
    i = int(coverage.argmin())
    return {"target": c, "fixed_cap": m, "p_grid_size": len(p),
            "minimum_coverage": float(coverage[i]), "at_p": float(p[i]),
            "max_lower_error": float(lower_error.max()),
            "max_upper_error": float(upper_error.max())}


def optional_cp_example(p=.5, max_n=40):
    # Stop at the first CP interval excluding p, or max_n. Exact state recursion.
    active = {0: 1.0}
    bad = good = 0.0
    for n in range(1, max_n+1):
        nxt = {}
        for old, mass in active.items():
            for x, prob in ((0, 1-p), (1, p)):
                h = old+x
                lo = beta.ppf(.025, h, n-h+1) if h else 0
                hi = beta.ppf(.975, h+1, n-h) if h < n else 1
                z = mass*prob
                if p < lo or p > hi:
                    bad += z
                elif n == max_n:
                    good += z
                else:
                    nxt[h] = nxt.get(h, 0)+z
        active = nxt
    assert abs(good+bad-1) < 1e-12
    return {"scope": "Illustrative data-dependent censoring, not the actual runtime law",
            "p": p, "max_n": max_n, "coverage": good, "noncoverage": bad}


def collector_fixtures():
    # Execute the actual collector function only, avoiding imports of simulators.
    tree = ast.parse(SOURCE.read_text())
    fn = next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == "check_setting")
    env = dict(os=os, json=json, hashlib=hashlib, math=math,
               COUNTERS=("proposals", "poisson_accept", "theta_accept", "paths", "selected_SA", "overflow",
                         "hits", "boundary", "hits_lo", "hits_hi", "rounding_excess"),
               HIT_KEYS={"batch", "proposal_in_batch", "boundary", "theta", "recorded"},
               PARAMS=("s", "f", "sigma", "rho", "p_c", "delta"))
    exec(compile(ast.Module(body=[fn], type_ignores=[]), str(SOURCE), "exec"), env)
    b = dict(batch=4, hit_stop=3, prefix_batches=1)
    st = dict(index=0, pop="fixture", outer="null/0", n=30, proposal_budget=16, worker=0, batches=4)
    metric = {"outers": {"fixture|null/0": {"recorded": [4, 3, 1]}}}
    binding = {"fixture": True}
    cases = [
        ("hit_with_overshoot", "complete", "hits", 3, [(0, 0), (1, 1), (2, 0), (2, 3)]),
        ("hit_at_first_possible_suffix_time", "complete", "hits", 2, [(0, 0), (1, 0), (1, 1)]),
        ("fixed_cap", "complete", "budget", 4, [(0, 0), (1, 1)]),
        ("censored", "censored", None, 3, [(0, 0), (1, 1)]),
        ("failed", "failed", None, 3, [(0, 0), (1, 1)]),
        ("running", "running", None, 3, [(0, 0), (1, 1)]),
        ("zero_suffix_hits", "complete", "budget", 4, [(0, 0)]),
    ]
    out = {}
    with tempfile.TemporaryDirectory() as tmp:
        for name, status, stop, nb, positions in cases:
            recs = [dict(batch=bi, proposal_in_batch=pi, boundary=False,
                         theta={k: .5 for k in env["PARAMS"]}, recorded=[4, 3, 1]) for bi, pi in positions]
            raw = b"".join((json.dumps(r)+"\n").encode() for r in recs)
            (Path(tmp)/"s0000_hits.jsonl").write_bytes(raw)
            S = dict(binding=binding, index=0, status=status, batches_done=nb, cpu_seconds=4.0,
                     journal_bytes=len(raw), journal_sha256=hashlib.sha256(raw).hexdigest(),
                     proposals=4*nb, poisson_accept=4*nb, theta_accept=4*nb, paths=4*nb,
                     selected_SA=len(recs), overflow=0, hits=len(recs), boundary=0,
                     hits_lo=len(recs), hits_hi=len(recs), rounding_excess=0)
            if stop:
                S["stop"] = stop
            if status == "failed":
                S["failure"] = "fixture failure"
            (Path(tmp)/"s0000.json").write_text(json.dumps(S))
            row, errors = env["check_setting"](st, b, binding, metric, tmp)
            assert errors == [], (name, errors)
            if stop == "hits":
                t = row["suffix_proposals_to_cap"]
                expected = [beta.ppf(.025, 2, t-1), beta.ppf(.975, 2, t-2) if t > 2 else 1]
                assert np.allclose(row["ci95_suffix"], expected, atol=1e-14, rtol=0)
                assert "observed_cpu_hours_to_crossing_batch" in row
                assert "projected_cpu_hours_to_2000" not in row
            else:
                h, n = row["suffix_hits"], row["suffix_proposals"]
                expected = [beta.ppf(.025, h, n-h+1) if h else 0,
                            beta.ppf(.975, h+1, n-h) if h < n else 1]
                assert np.allclose(row["ci95_suffix"], expected, atol=1e-14, rtol=0)
            out[name] = {k: v for k, v in row.items()
                         if k.startswith(("prefix_", "suffix_", "ci", "observed_", "projected_"))}
    return out


result = {
    "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "versions": {"numpy": np.__version__, "scipy": scipy.__version__},
    "scope": "Exact finite distributions and tiny synthetic collector records; no population trajectories",
    "curtailed_coverage": [curtailed_check(c, m) for c, m in ((1, 5), (2, 5), (3, 10), (5, 20), (10, 30), (20, 100))],
    "informative_censoring_counterexample": optional_cp_example(),
    "collector_fixtures": collector_fixtures(),
}
Path(__file__).with_name("checks.json").write_text(json.dumps(result, indent=2)+"\n")
print(json.dumps({k: v for k, v in result.items() if k != "collector_fixtures"}, indent=2))
print("collector fixtures:", list(result["collector_fixtures"]))
