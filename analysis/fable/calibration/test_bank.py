"""Limiting-case tests for the alternative generators in bank.py (protocol §3.2; Astra 0.8
review). Run from repo root:
    python3 analysis/fable/calibration/test_bank.py
Each check prints PASS/FAIL; the script exits non-zero on any failure."""
import sys
import numpy as np
sys.path.insert(0, "analysis/fable/calibration")
from bank import designs, simulate_chunk, drift_offset, DETECT

fails = 0


def check(name, ok, detail=""):
    global fails
    fails += not ok
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


def run(name, n=40_000, seed=11, **kw):
    return simulate_chunk(D[name], "ar_cat", n, np.random.default_rng(seed), **kw)


D = designs()
pops = ("wood_turtle_B", "hawaiian_crow", "wild_dog")

# 1. Zero deterioration recovers ar_cat exactly (same seed), for every M_D form
for name in pops:
    base = run(name)
    for form in ("linear", "accel", "step"):
        md = run(name, drift={"form": form, "hi": 0.0})
        check(f"M_D {form} hi=0 equals ar_cat ({name})",
              np.array_equal(base[0], md[0]) and np.array_equal(base[3], md[3]))

# 2. beta = 0 in a mixture recovers its M_D component exactly
for form in ("linear", "accel", "step"):
    a = run("marmot", drift={"form": form, "hi": 2.0})
    b = run("marmot", drift={"form": form, "hi": 2.0}, beta=0.0)
    check(f"M_A+M_D beta=0 equals M_D {form}", np.array_equal(a[0], b[0]) and np.array_equal(a[3], b[3]))

# 3. Perfect detection recovers the latent-count generator exactly, and recorded = latent
for name in pops:
    base = run(name)
    mo = run(name, detect=lambda n: np.ones(np.shape(n)))
    check(f"M_O p=1 equals ar_cat ({name})",
          np.array_equal(base[0], mo[0]) and np.array_equal(base[3], mo[3])
          and np.array_equal(mo[1]["latent"], mo[0]))

# 4. M_O: recorded never exceeds latent after the first census; first recorded count is n0;
#    latent start is round(n0 / p(n0)); selection uses recorded counts only
for law in ("lown", "uniform"):
    rec, p, over, sel = run("golden_plover", detect=DETECT[law])
    lat = p["latent"]; n0 = int(D["golden_plover"]["counts"][0])
    check(f"M_O {law}: recorded <= latent", (rec[:, 1:] <= lat[:, 1:]).all())
    check(f"M_O {law}: first recorded = n0, latent start", (rec[:, 0] == n0).all()
          and (lat[:, 0] == round(n0 / float(DETECT[law](n0)))).all(), f"latent N0 {int(lat[0, 0])}")
    rule = (rec[:, 1:-1] > 1).all(axis=1) & (rec[:, -1] <= 1) & ~over
    check(f"M_O {law}: selection on recorded counts", np.array_equal(sel, rule))
    check(f"M_O {law}: some selected paths are latently extant at the endpoint",
          (lat[sel, -1] > 1).any(), f"{int((lat[sel, -1] > 1).sum())} of {int(sel.sum())}")

# 5. Deterioration offsets match the protocol forms exactly
span = 18
check("drift linear = d*t", np.isclose(drift_offset("linear", 1.8, 0, 9, span), 0.9))
check("drift accel = d*t^2/span", np.isclose(drift_offset("accel", 1.8, 0, 9, span), 1.8 * 81 / 324))
check("drift step", np.array_equal(drift_offset("step", np.array([1.0, 1.0]), np.array([5, 10]), 7, span),
                                   np.array([1.0, 0.0])))

# 6. A positive shift lowers selected pre-terminal abundance relative to the null (direction)
base = run("ms_woodpecker", n=200_000, seed=3)
md = run("ms_woodpecker", n=200_000, seed=3, drift={"form": "linear", "hi": 2.0})
fa = base[3].mean(); fm = md[3].mean()
check("M_D raises the matched-extinction selection rate", fm > fa, f"null {fa:.4f}, M_D {fm:.4f}")

# 7. Shift and step-time provenance are recorded and in range
rec, p, over, sel = run("marmot", drift={"form": "step", "hi": 2.0})
yrs = D["marmot"]["years"]
check("M_D step provenance", (p["md_shift"] >= 0).all() and (p["md_shift"] <= 2).all()
      and (p["md_tau"] >= 1).all() and (p["md_tau"] <= yrs[-1] - yrs[0]).all())

print("FAILURES:", fails)
sys.exit(1 if fails else 0)
