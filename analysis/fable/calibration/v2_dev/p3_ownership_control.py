"""Ownership negative control for the Stage 1b round-3 runner (design 9h; Codex board 2422, acceptance case 4).
The same omitted-listing scenario runs against the bound round-2 runner (1e35b94a, from git) and the candidate runner:
one range claimed by owner A, its setting planned under the setting lock while the global queue/ and claimed/ listings
return nothing (the suspected production fault), then owner B claims; the candidate also faces every listing omitted. The bound runner republishes A's live range and admits B beside A; the candidate must not. Codex's
own reproduction (analysis/astra/w2_duplicate_review_20261027), which drives two shard engines over the republished range
to a doubled journal, is also run unchanged against the bound runner. Run from the repository root:
  python analysis/fable/calibration/v2_dev/p3_ownership_control.py OUT_JSON
Exit 0 only when the bound runner fails both and the candidate passes."""
import hashlib, importlib.util, json, os, shutil, subprocess, sys, tempfile, time

V2 = "analysis/fable/calibration/v2_dev"
BOUND = ("a839545", "1e35b94ab3811cc0ddded21aeaa5258120500c9e60f02dd5a6ee0c9c89d50d75")
CODEX = "analysis/astra/w2_duplicate_review_20261027/reproduce_duplicate_path.py"


def load(path, name):
    sys.path.insert(0, os.path.dirname(path))
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m); sys.path.pop(0)
    return m


def scenario(p3, new, omit_all=False):
    d = tempfile.mkdtemp(prefix="ownership_control_"); run = os.path.join(d, "run"); sdir = os.path.join(run, "sets", "s00001")
    for x in ("queue", "claimed", "workers/dead", "sets/s00001"):
        os.makedirs(os.path.join(run, x))
    st = {"dir": "s00001", "index": 1, "wave": "W2", "pilot": None, "cap_batches": 100, "rate": 1.0, "prior_hpb": 1.0}
    b = {"min_shard_cpu_h": 0.0, "target_wall_h": 24.0, "max_inflight": 1, "overshoot": 1.15}
    plan = (lambda: p3.plan(st, sdir, run, b, "planner")) if new else (lambda: p3.plan(st, sdir, run, b))
    with p3.held(sdir, "seed"):
        plan()
    first = sorted(os.listdir(os.path.join(run, "queue")))
    a = p3.claim(run, "ownerA", "W2", deadline=time.time() + 10)
    real = p3.ls
    p3.ls = lambda path: [] if omit_all or os.path.basename(path) in ("queue", "claimed") else real(path)
    try:
        with p3.held(sdir, "planner", patience=5, deadline=time.time() + 10):
            plan()
    finally:
        p3.ls = real
    republished = sorted(os.listdir(os.path.join(run, "queue")))
    bb = p3.claim(run, "ownerB", "W2", deadline=time.time() + 10)
    out = {"first_hints": first, "owner_a": a if not new else list(a), "republished_hints": republished,
           "owner_b": (list(bb) if new and bb else bb), "claim_entries": sorted(os.listdir(os.path.join(run, "claimed")))}
    if new:
        out["execution_records"] = sorted(os.listdir(os.path.join(sdir, "x")))
    out["second_writer_admitted"] = bb is not None
    shutil.rmtree(d)
    return out


def main(out_path):
    tmp = tempfile.mkdtemp(prefix="ownership_bound_"); bdir = os.path.join(tmp, V2); os.makedirs(bdir)
    src = subprocess.run(["git", "show", f"{BOUND[0]}:{V2}/p3_stage1b.py"], capture_output=True, check=True).stdout
    if hashlib.sha256(src).hexdigest() != BOUND[1]:
        raise SystemExit("git copy is not the bound runner")
    open(os.path.join(bdir, "p3_stage1b.py"), "wb").write(src)
    for f in ("p2_stage1a.py", "p1_sampler.py"):
        shutil.copy(os.path.join(V2, f), bdir)
    cand = os.path.join(V2, "p3_stage1b.py")
    res = {"bound_runner_sha256": BOUND[1], "candidate_runner_sha256": hashlib.sha256(open(cand, "rb").read()).hexdigest()}
    res["bound"] = scenario(load(os.path.join(bdir, "p3_stage1b.py"), "p3_bound"), False)
    cm = load(cand, "p3_candidate")
    res["candidate"] = scenario(cm, True)
    res["candidate_all_listings_omitted"] = scenario(cm, True, omit_all=True)
    cdir = os.path.join(tmp, os.path.dirname(CODEX)); os.makedirs(cdir); shutil.copy(CODEX, cdir)
    r = subprocess.run([sys.executable, os.path.join(tmp, CODEX)], capture_output=True, text=True)
    res["codex_reproduction_on_bound"] = {"exit": r.returncode, "result": json.loads(r.stdout) if r.returncode == 0 else r.stderr[-2000:]}
    shutil.rmtree(tmp)
    res["control_ok"] = res["bound"]["second_writer_admitted"] and len(res["bound"]["claim_entries"]) == 2 and r.returncode == 0 \
        and all(not c["second_writer_admitted"] and c["republished_hints"] == [] and len(c["claim_entries"]) == 1
                and len(c["execution_records"]) == 1 for c in (res["candidate"], res["candidate_all_listings_omitted"]))
    json.dump(res, open(out_path, "w"), indent=1)
    print(json.dumps({k: res[k] for k in ("bound_runner_sha256", "candidate_runner_sha256", "control_ok")}))
    if not res["control_ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main(sys.argv[1])
