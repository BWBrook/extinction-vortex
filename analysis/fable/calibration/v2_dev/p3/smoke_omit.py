"""Smoke-only Stage 1b worker: p3_stage1b.py work with the global queue/ and claimed/ listings each omitting entries at
random (probability OMIT_P, default 0.3), the suspected NFS listing fault of W2 (design 9g). Run from the source root, as
s1b_node.pbs runs the runner: python -I analysis/fable/calibration/v2_dev/p3/smoke_omit.py work ARGS..."""
import os, random, sys
sys.path.insert(0, os.path.join(os.getcwd(), "analysis/fable/calibration/v2_dev"))
import p3_stage1b as p3

P, real, rng = float(os.environ.get("OMIT_P", "0.3")), p3.ls, random.Random()


def ls(path):
    out = real(path)
    return [n for n in out if rng.random() >= P] if os.path.basename(path) in ("queue", "claimed") else out


p3.ls = ls
if sys.argv[1] != "work":
    raise SystemExit("smoke_omit.py runs workers only")
try:
    p3.work(*sys.argv[2:])
except p3.OwnerUncertain as ex:
    print(f"owner uncertain, ending: {ex}", file=sys.stderr, flush=True)
    sys.exit(75)
