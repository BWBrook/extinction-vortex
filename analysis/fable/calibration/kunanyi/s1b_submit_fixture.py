"""Stub-scheduler fixtures for s1b_submit.sh (no PBS, no simulation), reusing the s1a_submit_fixture stubs. FIX_BASH selects
the shell; writes s1b_submit_fixture[_FIX_TAG].json beside itself. Keys: a (the wave's job array) and c (the collector)."""
import hashlib, importlib.util, json, os, pathlib, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
SUBMIT = HERE / "s1b_submit.sh"
src = (HERE / "s1a_submit_fixture.py").read_text()
STUBS = {}
exec(src[src.index("STUBS = {"):src.index("\n\n\ndef scenario")], {}, ns := {}) or STUBS.update(ns["STUBS"])
NJOBS, CPUS, WALL_H, CEIL, PRIOR = 520, 8, 48.0, 200000.0, 0.0


def scenario(steps):
    with tempfile.TemporaryDirectory() as td:
        t = pathlib.Path(td); fb = t / "bin"; fb.mkdir()
        for name, body in STUBS.items():
            (fb / name).write_text(f"#!{sys.executable}\n{body}"); (fb / name).chmod(0o755)
        vb = t / "vbase"; (vb / "src").mkdir(parents=True); (vb / "s1b").mkdir()
        (vb / "s1b/p3_settings.json").write_text('{"fixture": true}')
        envf = t / "env.sh"; envf.write_text(f'export PATH="{fb}:$PATH"; cd "$VBASE/src"\n')
        base = dict(os.environ, PBS_BIN=str(fb), S1A_ENV=str(envf), S1A_CONFIRM_SECS="0", FIX_STATE=str(t / "jobs.json"),
                    FIX_LEDGER=str(t / "ledger.jsonl"), FIX_CALLS=str(t / "calls.jsonl"), FIX_QSELECT_CALLS=str(t / "qselect.n"))
        R = vb / "s1b/run/submit_W1"; J = R / "submit_journal.tsv"
        ledger = lambda: [json.loads(x) for x in (t / "ledger.jsonl").read_text().splitlines()] if (t / "ledger.jsonl").exists() else []
        runs = []
        for step in steps:
            if "finish" in step or "expire" in step:
                jobs = json.loads((t / "jobs.json").read_text())
                for i in step.get("finish", []):
                    jobs[i]["state"] = "F"
                jobs = [j for k, j in enumerate(jobs) if k not in step.get("expire", [])]
                (t / "jobs.json").write_text(json.dumps(jobs))
            for line in step.get("operator", []):
                J.open("a").write(line.format(**{f"id{k}": j["id"] for k, j in enumerate(ledger())},
                                              **{"name_a": next((l.split()[2] for l in J.read_text().splitlines() if l.split()[1] == "a"), "")}) + "\n")
            env = dict(base, **step.get("env", {}))
            before = len((t / "calls.jsonl").read_text().splitlines()) if (t / "calls.jsonl").exists() else 0
            args = [os.environ.get("FIX_BASH", "bash"), str(SUBMIT), str(vb), "p3_settings.json", "run", "W1", str(NJOBS), str(CPUS),
                    "48:00:00", str(CEIL), str(PRIOR)] + ([step["mode"]] if step.get("mode") else [])
            p = subprocess.run(args, env=env, capture_output=True, text=True)
            after = len((t / "calls.jsonl").read_text().splitlines()) if (t / "calls.jsonl").exists() else 0
            runs.append({"mode": step.get("mode", "new"), "rc": p.returncode, "qsub_calls": after - before,
                         "stderr": [l.replace(td, "<tmp>") for l in p.stderr.strip().splitlines()[-1:]]})
        led = ledger(); arrays = [j for j in led if j["name"].endswith("_a")]; coll = [j for j in led if j["name"].endswith("_c")]
        deps = []
        if coll:
            a = coll[0]["args"]; deps = a[a.index("-W") + 1].split(":", 1)[1].split(":") if "-W" in a else []
        jflag = [j["args"][j["args"].index("-J") + 1] for j in arrays]
        return {"runs": runs, "arrays_created": len(arrays), "array_ranges": jflag, "collectors_created": len(coll),
                "collector_depends_on": deps, "array_ids": [j["id"] for j in arrays],
                "allocated_cpu_hours_bound": len(arrays) * NJOBS * CPUS * WALL_H + len(coll) * 8 + PRIOR,
                "lock_released": not (R / ".submit.lock").exists()}


def ok(r, rcs, calls, arrays, coll, dep_on_array=True, lock=True):
    good = [x["rc"] == 0 for x in r["runs"]] == rcs and [x["qsub_calls"] for x in r["runs"]] == calls \
        and r["arrays_created"] == arrays and r["collectors_created"] == coll and r["lock_released"] is lock
    if arrays:
        good = good and r["array_ranges"] == [f"0-{NJOBS - 1}"] * arrays
    if coll:
        good = good and r["collector_depends_on"] == (r["array_ids"][:1] if dep_on_array else [])
    return good and r["allocated_cpu_hours_bound"] <= CEIL + 8


fail = lambda at, mode, **kw: {"env": dict({"FIX_FAIL_AT": str(at), "FIX_FAIL_MODE": mode}, **kw)}
R = {
    "normal_then_duplicate_then_resume": scenario([{}, {}, {"mode": "resume"}]),
    "array_rejected_held_until_operator_rejects": scenario([fail(1, "reject"), {"mode": "resume"},
                                                            {"operator": ["rejected a {name_a} manual: tracejob shows no job"], "mode": "resume"}]),
    "array_reply_lost_reconciled_at_once": scenario([fail(1, "ambiguous")]),
    "array_reply_lost_history_expired_no_replacement": scenario([
        fail(1, "ambiguous_expired"), {"mode": "resume"},
        {"operator": ["accepted a {name_a} {id0} manual: accounting log", "terminal a {id0} manual: accounting log"], "mode": "resume"}]),
    "collector_query_fails_then_resume": scenario([{"env": {"FIX_QSTAT_FAIL": "0"}}, {"mode": "resume"}]),
    "array_finished_before_collector": scenario([fail(2, "reject"),
                                                 {"operator": ["rejected c x manual: tracejob shows no job"], "finish": [0], "mode": "resume"}]),
    "preflight_refused": scenario([{"env": {"FIX_PREFLIGHT_RC": "1"}}]),
}
checks = {
    "normal_then_duplicate_then_resume": ok(R["normal_then_duplicate_then_resume"], [True, False, True], [2, 0, 0], 1, 1),
    "array_rejected_held_until_operator_rejects": ok(R["array_rejected_held_until_operator_rejects"], [False, False, True], [1, 0, 2], 1, 1),
    "array_reply_lost_reconciled_at_once": ok(R["array_reply_lost_reconciled_at_once"], [True], [2], 1, 1),
    "array_reply_lost_history_expired_no_replacement": ok(R["array_reply_lost_history_expired_no_replacement"],
                                                          [False, False, True], [1, 0, 1], 1, 1, dep_on_array=False),
    "collector_query_fails_then_resume": ok(R["collector_query_fails_then_resume"], [False, True], [1, 1], 1, 1),
    "array_finished_before_collector": ok(R["array_finished_before_collector"], [False, True], [2, 1], 1, 1, dep_on_array=False),
    "preflight_refused_before_any_qsub": ok(R["preflight_refused"], [False], [0], 0, 0),
}
bv = subprocess.run([os.environ.get("FIX_BASH", "bash"), "-c", "echo $BASH_VERSION"], capture_output=True, text=True).stdout.strip()
out = {"scope": __doc__, "bash_version": bv, "submit_sha256": hashlib.sha256(SUBMIT.read_bytes()).hexdigest(), "checks": checks,
       "all_ok": all(checks.values()), "scenarios": R}
tag = os.environ.get("FIX_TAG", "")
(HERE / f"s1b_submit_fixture{('_' + tag) if tag else ''}.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps({"bash_version": bv, "checks": checks, "all_ok": out["all_ok"]}, indent=1))
sys.exit(0 if out["all_ok"] else 1)
