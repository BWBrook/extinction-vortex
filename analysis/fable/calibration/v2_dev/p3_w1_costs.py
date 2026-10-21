"""W1 round-1 cost diagnosis (no sampling, no fits): actual against projected worker CPU-hours per setting.
  p3_w1_costs.py COLLECT_W1 SETTINGS PILOT_COLLECT OUT_JSON
Projection (design section 7, p2_inventory): the Stage 1a cost rule (p2_report.cost) for each pilot setting; each
(population, scenario, n) cell's 10 pilot outers (trials 0-9) stand for its 200, so an unseen outer's expectation is
its cell's pilot mean. For each completed setting the realised cost to K is split into throughput (CPU per batch,
against the bound rate) and hit rate (hits per batch to the K-th hit, against the cell prior), separately for pilot
and unseen outers. Incomplete settings are priced at their cell's mean realised cost (or more, if already spent)."""
import json, math, sys
from collections import defaultdict
import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from p2_report import cost

K, BATCH = 2000, 20000


def cell(st):
    return st["pop"], st["outer"].split("/")[0], st["n"]


def main(collect_json, settings_json, pilot_json, out):
    c = json.load(open(collect_json)); b = json.load(open(settings_json)); pc = json.load(open(pilot_json))
    by_dir = {s["dir"]: s for s in b["settings"]}
    proj = {}
    for r in pc["rows"]:
        kind, pt, lo, hi = cost(r)
        proj[r["index"]] = pt if pt is not None else lo
    cellproj = defaultdict(list)
    for s in b["settings"]:
        if s["library"] == "primary" and s["index"] in proj and proj[s["index"]] is not None:
            cellproj[cell(s)].append(proj[s["index"]])
    cellmean = {k: float(np.mean(v)) for k, v in cellproj.items()}
    rows, real = [], defaultdict(list)
    for r in c["rows"]:
        st = by_dir[r["dir"]]; pl = st["pilot"]; p0 = pl["batches_done"] if pl else 0
        trial = int(st["outer"].split("/")[1]); pilot_cpu = pl["cpu_seconds"] / 3600 if pl else 0.0
        spent = r.get("useful_cpu_h", 0.0) + r.get("discarded_cpu_h", 0.0) - pilot_cpu     # collector's useful includes the pilot
        x = {"dir": r["dir"], "n": st["n"], "cell": cell(st), "pilot_outer": trial < 10, "library": st["library"],
             "status": r["status"], "spent_w1": spent, "pilot_cpu": pilot_cpu,
             "projected": proj.get(st["index"]) if trial < 10 else cellmean.get(cell(st))}
        if r["status"] == "COMPLETE" and r.get("kth_hit") is not None and r["prefix_end_batch"] > p0:
            nb = r["kth_hit"] + 1
            cpb = r["useful_cpu_h"] / r["prefix_end_batch"]
            x.update(actual=nb * cpb + r.get("discarded_cpu_h", 0.0), throughput_ratio=cpb / (BATCH / st["rate"] / 3600),
                     hit_ratio=(K / nb) / st["prior_hpb"] if st["prior_hpb"] else None,
                     discard_share=r.get("discarded_cpu_h", 0.0) / (spent + pilot_cpu) if spent + pilot_cpu else 0.0)
            real[x["cell"]].append(x["actual"])
        rows.append(x)
    cellreal = {k: float(np.mean(v)) for k, v in real.items()}

    def summ(sel):
        done = [x for x in sel if "actual" in x]
        med = lambda k: float(np.median([x[k] for x in done if x.get(k) is not None])) if done else None
        a, p = sum(x["actual"] for x in done), sum(x["projected"] for x in done if x["projected"] is not None)
        return {"settings": len(sel), "complete_resolved": len(done), "actual_cpu_h": a, "projected_cpu_h": p,
                "actual_over_projected": a / p if p else None, "median_throughput_ratio": med("throughput_ratio"),
                "median_hit_ratio": med("hit_ratio"), "median_discard_share": med("discard_share")}
    groups = {}
    for n in (0, 30):
        for po in (True, False):
            groups[f"n={n} {'pilot' if po else 'unseen'} outers"] = summ([x for x in rows if x["n"] == n and x["pilot_outer"] == po
                                                                          and x["library"] == "primary"])
    remain = []
    for x in rows:
        if x["status"] == "incomplete":
            m = cellreal.get(x["cell"], x["projected"] or 0.0)
            remain.append(max(m, x["spent_w1"] * 1.25))
    out_ = {"scope": __doc__, "collect_sha_binding": c["binding"], "groups": groups,
            "w1_spent_round1_cpu_h": sum(x["spent_w1"] for x in rows),
            "incomplete": len(remain), "incomplete_restart_estimate_cpu_h": float(sum(remain)),
            "cells": {"|".join(map(str, k)): {"projected_mean": cellmean.get(k), "realised_mean_complete": v,
                                               "complete": len(real[k])} for k, v in cellreal.items()}}
    json.dump(out_, open(out, "w"), indent=1)
    for k, v in groups.items():
        print(k, {a: (round(b_, 3) if isinstance(b_, float) else b_) for a, b_ in v.items()})
    print("incomplete", len(remain), "restart estimate CPU-h", round(sum(remain)))


if __name__ == "__main__":
    main(*sys.argv[1:])
