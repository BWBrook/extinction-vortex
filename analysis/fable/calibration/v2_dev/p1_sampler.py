"""Bounded informative-sampler prototype (notes/astra_informative_reference_proposal_20261014.md; design doc §8).
No fits, no full banks, no kunanyi. Target, for one population and one outer i:
    pi_b(theta) L(E|theta) m0(N|theta) 1{S,A} 1{C(N) in B_i}
Sampler: theta ~ frozen prior; accept with L(E|theta)/M_E (Poisson factor first, then binomial with an independent
uniform); simulate ONE null path; retain if S, A and the closed C-ball hold; otherwise restart theta.
Path dynamics are the frozen bank.simulate_chunk with only draw_params replaced by the supplied theta arrays.
Run from the frozen source root.
  prepare MANIFEST BASE S0_INPUTS S0_FULLDIR OUT_JSON   bind settings, E, radii, streams, schedule
  test    MANIFEST BASE BOUND_JSON                       sampler/path/law tests (exits non-zero on failure)
  scan    MANIFEST BASE BOUND_JSON OUT_JSON              closed-ball counts and retention forecasts from the existing bank
  pilot   MANIFEST BASE BOUND_JSON OUT_JSON MAX_SECONDS  balanced capped pilot (one worker, single-threaded numerics)
"""
import hashlib, json, os, platform, resource, sys, time
import numpy as np
import scipy
from scipy.special import xlogy, xlog1py
sys.path.insert(0, "analysis/fable/calibration")
import bank
from bank import designs, calib_features, load_bank
from validate import manifest_digest

HERE = os.path.dirname(os.path.abspath(__file__))
PAIRS = (("wild_dog", "null_prior_predictive/0"), ("wild_dog", "null_low_s/0"),
         ("hawaiian_crow", "null_prior_predictive/0"), ("hawaiian_crow", "null_low_s/0"))
KINDS = (("n0", 0, None), ("noisy", 30, 0), ("ideal", 30, 0), ("noisy", 300, 1), ("ideal", 300, 1))
SCEN_INDEX = {"null_prior_predictive": 0, "null_low_s": 1}
CAP_PROPOSALS, CAP_PATHS, BATCH = 10 ** 6, 10 ** 5, 50_000
LOG_TOL = 1e-9                       # rounding excess allowed above the analytic bound (counted, never hidden)
GH_X, GH_W = np.polynomial.hermite_e.hermegauss(40)
GH_W = GH_W / GH_W.sum()


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def rate_functionals(p):
    ls = np.log(p["s"] / (1 - p["s"]))
    es = np.zeros(np.shape(ls))
    for x, w in zip(GH_X, GH_W):
        es = es + w / (1 + np.exp(-(ls + p["sigma"] * x)))
    keep = 1 - p["delta"] * p["p_c"]
    return keep * es, keep * p["f"]


def log_factors(u, v, n, k, r):
    """Binomial and Poisson log acceptance factors h - H (each <= 0 up to rounding); k, r may be real (ideal)."""
    if n == 0:
        z = np.zeros(np.shape(u)); return z, z
    hb = xlogy(k, u) + xlog1py(n - k, -u) - (xlogy(k, k / n) + xlog1py(n - k, -k / n))
    hp = xlogy(r, v) - n * v - (xlogy(r, r / n) - r)
    return hb, hp


def simulate_given(design, variant, theta, rng):
    """Frozen simulate_chunk with draw_params replaced by the supplied per-path theta arrays."""
    n = len(theta["s"])
    orig = bank.draw_params
    bank.draw_params = lambda variant_, n_, rng_: {**{k: np.asarray(theta[k], float).copy() for k in theta},
                                                   "nu": np.full(n, np.inf)}
    try:
        return bank.simulate_chunk(design, variant, n, rng)
    finally:
        bank.draw_params = orig


def ball(c_new, q, keep, mad, radius):
    d = np.sqrt((((c_new[:, keep] / mad[keep]) - q) ** 2).sum(1))       # declared float64 routine
    lo, hi = np.nextafter(radius, -np.inf), np.nextafter(radius, np.inf)
    return {"in": d <= radius, "boundary": d == radius, "in_lo": d <= lo, "in_hi": d <= hi}


def setting_list():
    out = []
    for pi, (pop, okey) in enumerate(PAIRS):
        for kind, n, ni in KINDS:
            out.append({"index": len(out), "pop": pop, "outer": okey, "kind": kind, "n": n, "n_index": ni})
    return out


def prepare(man_path, base, s0_inputs, s0_full, out):
    s0 = json.load(open(s0_inputs)); settings = setting_list()
    radii = {}
    for pop, okey in PAIRS:
        rows = {r["outer"]: r for r in json.load(open(os.path.join(s0_full, f"s0_{pop}.json")))["rows"]}
        radii[f"{pop}|{okey}"] = rows[okey]["kth"]
    for st in settings:
        name, trial = st["outer"].split("/")
        st["outer_recorded"] = s0["outers"][st["outer"]]["pops"][st["pop"]]["recorded"]
        st["radius"] = radii[f"{st['pop']}|{st['outer']}"]
        if st["kind"] == "n0":
            st["E"] = {"n": 0, "k": 0, "r": 0}
        else:
            cell = 4 * st["n_index"] + SCEN_INDEX[name]
            e = s0["E"][f"{cell}/{trial}/{st['pop']}"]
            st["E"] = ({"n": e["n"], "k": e["k"], "r": e["r"]} if st["kind"] == "noisy"
                       else {"n": e["n"], "k": e["n"] * e["sbar_true"], "r": e["n"] * e["fbar_true"]})
    man = json.load(open(man_path))
    bind = {"prototype": "informative-sampler throughput pilot (no fits)", "manifest_digest": manifest_digest(man_path),
            "s0_inputs_sha256": sha(s0_inputs), "s0_output_sha256": {p: sha(os.path.join(s0_full, f"s0_{p}.json")) for p, _ in PAIRS},
            "settings": settings, "caps": {"proposals": CAP_PROPOSALS, "paths": CAP_PATHS, "batch_proposals": BATCH},
            "schedule": "round-robin over settings in index order; one batch of up to BATCH prior proposals per setting per round "
                        "(truncated to the remaining proposal cap); a setting stops once either cap is reached; the pilot stops at MAX_SECONDS",
            "stream": "numpy.random.default_rng([20261015, setting_index, round]); consumption order: draw_params(B), "
                      "Poisson uniforms(B), binomial uniforms(B), then simulate_given(accepted)",
            "acceptance": "log U < log-factor; Poisson factor first, then binomial on survivors with an independent uniform; "
                          f"log-factor in (0, {LOG_TOL}] counted as rounding excess, larger is a bound violation that stops the setting",
            "ball": "closed: float64 sqrt(sum(((C[keep]/mad[keep]) - q)^2)) <= Stage 0 full-precision K-th radius; boundary (==) and "
                    "adjacent-float radii counted separately; frozen primary-bank mask and MAD",
            "threads": "OMP/OPENBLAS/MKL threads 1; one worker",
            "runtime": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
            "helper_sha256": sha(os.path.abspath(__file__)), "bank_draws_per_population": 2 * 10 ** 9}
    json.dump(bind, open(out, "w"), indent=1)
    print("bound", out, sha(out), len(settings), "settings")


def check_binding(man_path, b):
    if b["manifest_digest"] != manifest_digest(man_path) or b["helper_sha256"] != sha(os.path.abspath(__file__)) \
            or b["runtime"] != {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__}:
        raise SystemExit("refused: manifest, helper bytes or runtime differ from the bound file")


def metric(man, base, pop):
    bk = load_bank(os.path.join(base, man["bankdir"]), man["variant"], pop)
    c = calib_features(bk["rec"]); mad = np.median(np.abs(c - np.median(c, 0)), 0); keep = mad > 0
    return bk, c, keep, mad


def test(man_path, base, bound_path):
    man = json.load(open(man_path)); b = json.load(open(bound_path)); check_binding(man_path, b)
    des = designs(); res = {}
    # 1. parameter-fed wrapper reproduces the frozen generator at fixed parameters (same consumed stream)
    theta = {"s": 0.6, "f": 0.3, "sigma": 0.5, "rho": 0.4, "p_c": 0.03, "delta": 0.7}
    for pop in ("wild_dog", "hawaiian_crow"):
        n = 5000
        r1 = np.random.default_rng(99); a = bank.simulate_chunk(des[pop], man["variant"], n, r1, fixed=theta)
        r2 = np.random.default_rng(99); bank.draw_params(man["variant"], n, r2)        # consume as the frozen call does
        bb = simulate_given(des[pop], man["variant"], {k: np.full(n, v) for k, v in theta.items()}, r2)
        res[f"wrapper_matches_frozen_{pop}"] = bool(np.array_equal(a[0], bb[0]) and np.array_equal(a[2], bb[2]) and np.array_equal(a[3], bb[3]))
    # 2. analytic bound: maximum of h at u = k/n, v = r/n; no grid point exceeds it
    u = np.linspace(1e-6, 1 - 1e-6, 2001); v = np.linspace(1e-6, 3, 2001)
    worst = -np.inf
    for n, k, r in ((30, 0, 0), (30, 30, 7), (30, 12, 5), (300, 290, 40), (300, 0.3 * 300, 0.1 * 300)):
        hb, hp = log_factors(u, v, n, k, r)
        worst = max(worst, float(hb.max()), float(hp.max()))
    res["bound_max_log_factor"] = worst; res["bound_ok"] = worst <= LOG_TOL
    # 3. n = 0 accepts everything
    hb, hp = log_factors(u, v, 0, 0, 0); res["n0_accepts_all"] = bool((hb == 0).all() and (hp == 0).all())
    # 4. factorised rejection preserves the product acceptance probability (Monte Carlo, fixed theta)
    rng = np.random.default_rng(7); n, k, r = 30, 12, 5; uu, vv = 0.35, 0.2
    hb, hp = log_factors(np.array([uu]), np.array([vv]), n, k, r)
    p_target = float(np.exp(hb[0] + hp[0]))
    m = 2_000_000
    acc = (np.log(rng.random(m)) < hp[0]) & (np.log(rng.random(m)) < hb[0])
    res["factorised_acceptance"] = {"target": p_target, "observed": float(acc.mean()),
                                    "ok": abs(acc.mean() - p_target) < 5 * np.sqrt(p_target * (1 - p_target) / m)}
    # 5. joint-selection law on a two-state toy: restart theta after each failed path
    rng = np.random.default_rng(11); keepA = keepB = 0
    for _ in range(200):
        th = rng.integers(0, 2, 10_000)                                     # prior 0.5/0.5
        sel = rng.random(10_000) < np.where(th == 0, 0.1, 0.9)               # one path per theta
        keepA += int((sel & (th == 0)).sum()); keepB += int((sel & (th == 1)).sum())
    fa = keepA / (keepA + keepB)
    res["joint_selection_law"] = {"freq_A": fa, "target": 0.1, "wrong_hold_until_selected": 0.5, "ok": abs(fa - 0.1) < 0.005}
    # 6. ball boundary handling: a point exactly at the radius is in, and counted on the boundary
    q = np.array([0.0, 0.0]); keep = np.array([True, True]); mad = np.array([1.0, 1.0])
    cb = ball(np.array([[3.0, 4.0], [3.0, 4.000001]]), q, keep, mad, 5.0)
    res["ball_boundary"] = bool(cb["in"].tolist() == [True, False] and cb["boundary"].tolist() == [True, False])
    ok = all(v if isinstance(v, bool) else v.get("ok", True) for k2, v in res.items() if k2 != "bound_max_log_factor")
    res["all_ok"] = ok
    print(json.dumps(res, indent=1))
    if not ok:
        raise SystemExit("tests failed")


def scan(man_path, base, bound_path, out):
    man = json.load(open(man_path)); b = json.load(open(bound_path)); check_binding(man_path, b)
    t0 = time.time(); res = {"pairs": {}, "settings": {}}
    for pop in ("wild_dog", "hawaiian_crow"):
        bk, c, keep, mad = metric(man, base, pop)
        u_all, v_all = rate_functionals(bk)
        for st in b["settings"]:
            if st["pop"] != pop:
                continue
            q = calib_features(np.array([st["outer_recorded"]]))[0][keep] / mad[keep]
            bl = ball(c, q, keep, mad, st["radius"])
            key = f"{pop}|{st['outer']}"
            res["pairs"][key] = {"radius": st["radius"], "members_closed_ball": int(bl["in"].sum()),
                                 "boundary": int(bl["boundary"].sum()), "members_at_lower_adjacent_radius": int(bl["in_lo"].sum()),
                                 "members_at_upper_adjacent_radius": int(bl["in_hi"].sum()), "bank_rows": int(len(c))}
            E = st["E"]; hb, hp = log_factors(u_all[bl["in"]], v_all[bl["in"]], E["n"], E["k"], E["r"])
            fsum = float(np.exp(hb + hp).sum())
            res["settings"][str(st["index"])] = {**{k: st[k] for k in ("pop", "outer", "kind", "n")},
                                                 "forecast_retained_per_prior_proposal": fsum / b["bank_draws_per_population"],
                                                 "forecast_expected_hits_at_proposal_cap": fsum / b["bank_draws_per_population"] * CAP_PROPOSALS,
                                                 "ball_weight_sum": fsum}
        del bk, c, u_all, v_all
    res["seconds"] = round(time.time() - t0, 1); res["peak_rss_gb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6, 2)
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps(res["pairs"], indent=1)); print("scan s", res["seconds"], "peak GB", res["peak_rss_gb"])


def pilot(man_path, base, bound_path, out, max_seconds):
    man = json.load(open(man_path)); b = json.load(open(bound_path)); check_binding(man_path, b)
    t0 = time.time(); max_seconds = float(max_seconds); des = designs()
    metrics = {}
    for pop in ("wild_dog", "hawaiian_crow"):
        bk, c, keep, mad = metric(man, base, pop); metrics[pop] = (keep, mad); del bk, c
    st_all = b["settings"]
    stats = {st["index"]: {"proposals": 0, "poisson_accept": 0, "theta_accept": 0, "paths": 0, "selected_SA": 0, "overflow": 0,
                           "ball_hits": 0, "ball_boundary": 0, "ball_hits_lower_adjacent": 0, "ball_hits_upper_adjacent": 0,
                           "rounding_excess": 0, "bound_violation": False, "seconds": 0.0, "sample_theta": [], "sample_paths": [],
                           "stopped": None} for st in st_all}
    rnd = 0
    while True:
        active = [st for st in st_all if stats[st["index"]]["stopped"] is None]
        if not active:
            break
        for st in active:
            if time.time() - t0 > max_seconds:
                for s2 in st_all:
                    if stats[s2["index"]]["stopped"] is None:
                        stats[s2["index"]]["stopped"] = "time cap"
                break
            S = stats[st["index"]]; ts = time.time()
            B = min(BATCH, CAP_PROPOSALS - S["proposals"])
            rng = np.random.default_rng([20261015, st["index"], rnd])
            th = bank.draw_params(man["variant"], B, rng)
            up, ub = np.log(rng.random(B)), np.log(rng.random(B))
            E = st["E"]
            vbar = th["f"] * (1 - th["delta"] * th["p_c"])
            hp = (xlogy(E["r"], vbar) - E["n"] * vbar - (xlogy(E["r"], E["r"] / E["n"]) - E["r"])) if E["n"] else np.zeros(B)
            exc = hp > 0
            if (hp > LOG_TOL).any():
                S["bound_violation"] = True; S["stopped"] = "bound violation"; continue
            S["rounding_excess"] += int(exc.sum())
            okp = up < hp; S["poisson_accept"] += int(okp.sum())
            idx = np.flatnonzero(okp)
            sub = {k2: th[k2][idx] for k2 in ("s", "f", "sigma", "rho", "p_c", "delta")}
            if E["n"]:
                u, _ = rate_functionals(sub)
                hb = xlogy(E["k"], u) + xlog1py(E["n"] - E["k"], -u) - (xlogy(E["k"], E["k"] / E["n"]) + xlog1py(E["n"] - E["k"], -E["k"] / E["n"]))
                if (hb > LOG_TOL).any():
                    S["bound_violation"] = True; S["stopped"] = "bound violation"; continue
                S["rounding_excess"] += int((hb > 0).sum())
                okb = ub[idx] < hb
            else:
                okb = np.ones(len(idx), bool)
            acc = {k2: v[okb] for k2, v in sub.items()}
            na = int(okb.sum()); S["theta_accept"] += na; S["proposals"] += B
            room = CAP_PATHS - S["paths"]
            if na > room:
                acc = {k2: v[:room] for k2, v in acc.items()}; na = room
            if na:
                rec, p, over, sel = simulate_given(des[st["pop"]], man["variant"], acc, rng)
                S["paths"] += na; S["overflow"] += int(over.sum()); S["selected_SA"] += int(sel.sum())
                if sel.any():
                    keep, mad = metrics[st["pop"]]
                    q = calib_features(np.array([st["outer_recorded"]]))[0][keep] / mad[keep]
                    bl = ball(calib_features(rec[sel]), q, keep, mad, st["radius"])
                    S["ball_hits"] += int(bl["in"].sum()); S["ball_boundary"] += int(bl["boundary"].sum())
                    S["ball_hits_lower_adjacent"] += int(bl["in_lo"].sum()); S["ball_hits_upper_adjacent"] += int(bl["in_hi"].sum())
                    if len(S["sample_paths"]) < 20 and bl["in"].any():
                        S["sample_paths"] += rec[sel][bl["in"]][: 20 - len(S["sample_paths"])].astype(int).tolist()
                if len(S["sample_theta"]) < 50:
                    S["sample_theta"] += [{k2: float(v[j]) for k2, v in acc.items()} for j in range(min(na, 50 - len(S["sample_theta"])))]
            S["seconds"] += time.time() - ts
            if S["proposals"] >= CAP_PROPOSALS:
                S["stopped"] = "proposal cap"
            elif S["paths"] >= CAP_PATHS:
                S["stopped"] = "path cap"
        rnd += 1
    res = {"bound_sha256": sha(bound_path), "rounds": rnd, "wall_seconds": round(time.time() - t0, 1),
           "peak_rss_gb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6, 2), "settings": {}}
    for st in st_all:
        S = stats[st["index"]]
        S["theta_acceptance_rate"] = S["theta_accept"] / S["proposals"] if S["proposals"] else None
        S["seconds_per_path"] = S["seconds"] / S["paths"] if S["paths"] else None
        S["seconds_per_retained_path"] = S["seconds"] / S["ball_hits"] if S["ball_hits"] else None
        res["settings"][str(st["index"])] = {**{k: st[k] for k in ("pop", "outer", "kind", "n")}, **S}
    json.dump(res, open(out, "w"), indent=1)
    for k2, v in res["settings"].items():
        print(k2, v["pop"][:9], v["outer"][:16], v["kind"], v["n"], "prop", v["proposals"], "acc", v["theta_accept"], "paths", v["paths"],
              "SA", v["selected_SA"], "hits", v["ball_hits"], "bd", v["ball_boundary"], v["stopped"], round(v["seconds"], 1))
    print("wall", res["wall_seconds"], "peak GB", res["peak_rss_gb"])


if __name__ == "__main__":
    cmd, a = sys.argv[1], sys.argv[2:]
    {"prepare": prepare, "test": test, "scan": scan, "pilot": pilot}[cmd](*a)
