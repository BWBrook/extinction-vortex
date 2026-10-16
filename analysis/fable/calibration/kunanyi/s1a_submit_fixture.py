"""Stub-scheduler fixtures for s1a_submit.sh (no PBS, no simulation). Writes s1a_submit_fixture.json beside itself.
Each scenario runs the real script in a fresh directory with stub qsub/qselect/qstat (PBS_BIN) and a stub preflight
(S1A_ENV); qsub can reject (no job) or accept but lose its reply (job created, non-zero exit) at a chosen call."""
import json, os, pathlib, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
SUBMIT = HERE / "s1a_submit.sh"
NJOBS, CPUS, WALL_H, CEIL = 45, 8, 2.75, 1000.0
STUBS = {
    "qsub": r'''
import json, os, pathlib, sys
st, calls = pathlib.Path(os.environ["FIX_STATE"]), pathlib.Path(os.environ["FIX_CALLS"])
jobs = json.loads(st.read_text()) if st.exists() else []
n = (len(calls.read_text().splitlines()) if calls.exists() else 0) + 1
calls.open("a").write(json.dumps(sys.argv[1:]) + "\n")
a = sys.argv[1:]; at, mode = int(os.environ.get("FIX_FAIL_AT", "-1")), os.environ.get("FIX_FAIL_MODE", "")
if n == at and mode == "reject":
    sys.exit(7)
jid = f"{900000 + len(jobs)}.fixture"
jobs.append({"id": jid, "name": a[a.index("-N") + 1], "args": a, "state": "Q"}); st.write_text(json.dumps(jobs))
if n == at and mode == "ambiguous":
    sys.exit(1)
print(jid)
''',
    "qselect": r'''
import json, os, pathlib, sys
st = pathlib.Path(os.environ["FIX_STATE"]); jobs = json.loads(st.read_text()) if st.exists() else []
a = sys.argv[1:]; name = a[a.index("-N") + 1]
for j in jobs:
    if j["name"] == name and ("-x" in a or j["state"] != "F"):
        print(j["id"])
''',
    "qstat": r'''
import json, os, pathlib, sys
st = pathlib.Path(os.environ["FIX_STATE"]); jobs = {j["id"]: j for j in json.loads(st.read_text())}
a = sys.argv[1:]; j = jobs.get(a[-1])
if j is None or j["state"] == "F":
    sys.exit(35)
if "-f" in a:
    print("    Mail_Users = fixture\n    Mail_Points = ae")
''',
    "python": r'''
import os, sys
print('{"preflight": "%s"}' % ("passed" if os.environ.get("FIX_PREFLIGHT_RC", "0") == "0" else "refused"))
sys.exit(int(os.environ.get("FIX_PREFLIGHT_RC", "0")))
''',
}


def scenario(steps, prepare=None):
    with tempfile.TemporaryDirectory() as td:
        t = pathlib.Path(td); fb = t / "bin"; fb.mkdir()
        for name, body in STUBS.items():
            (fb / name).write_text(f"#!{sys.executable}\n{body}"); (fb / name).chmod(0o755)
        vb = t / "vbase"; (vb / "src").mkdir(parents=True); (vb / "s1a").mkdir()
        (vb / "s1a/settings.json").write_text('{"fixture": true}')
        envf = t / "env.sh"; envf.write_text(f'export PATH="{fb}:$PATH"; cd "$VBASE/src"\n')
        base = dict(os.environ, PBS_BIN=str(fb), S1A_ENV=str(envf), FIX_STATE=str(t / "jobs.json"), FIX_CALLS=str(t / "calls.jsonl"))
        R = vb / "s1a/main"
        if prepare:
            prepare(t, R)
        runs = []
        for step in steps:
            env = dict(base, **step.get("env", {}))
            before = len((t / "calls.jsonl").read_text().splitlines()) if (t / "calls.jsonl").exists() else 0
            if "finish" in step:
                jobs = json.loads((t / "jobs.json").read_text())
                for j in jobs[: step["finish"]]:
                    j["state"] = "F"
                (t / "jobs.json").write_text(json.dumps(jobs))
            args = ["bash", str(SUBMIT), str(vb), "settings.json", "main", str(step.get("njobs", NJOBS)), str(step.get("cpus", CPUS)),
                    "02:45:00", str(CEIL), "0.44"] + ([step["mode"]] if step.get("mode") else [])
            p = subprocess.run(args, env=env, capture_output=True, text=True)
            after = len((t / "calls.jsonl").read_text().splitlines()) if (t / "calls.jsonl").exists() else 0
            runs.append({"mode": step.get("mode", "new"), "rc": p.returncode, "qsub_calls": after - before,
                         "stderr": p.stderr.strip().splitlines()[-1:] if p.stderr.strip() else []})
        jobs = json.loads((t / "jobs.json").read_text()) if (t / "jobs.json").exists() else []
        nodes = [j for j in jobs if "_j" in j["name"]]; coll = [j for j in jobs if j["name"].endswith("_c")]
        owners = []
        for j in nodes:
            v = dict(x.split("=", 1) for x in j["args"][j["args"].index("-v") + 1].split(","))
            owners += range(int(v["JOB"]) * int(v["JOBCPUS"]), (int(v["JOB"]) + 1) * int(v["JOBCPUS"]))
        deps = []
        if coll:
            a = coll[0]["args"]
            deps = a[a.index("-W") + 1].split(":", 1)[1].split(":") if "-W" in a else []
        journal = (R / "submit_journal.tsv").read_text().splitlines() if (R / "submit_journal.tsv").exists() else []
        live_nodes = [j["id"] for j in nodes if j["state"] != "F"]
        return {"runs": runs, "node_jobs": len(nodes), "unique_node_names": len({j["name"] for j in nodes}),
                "collectors": len(coll), "workers_with_one_owner": len(owners) == len(set(owners)) == NJOBS * CPUS if nodes else None,
                "collector_depends_on": len(deps), "collector_covers_unfinished_nodes": set(deps) == set(live_nodes) if coll else None,
                "allocated_cpu_hours_bound": len(nodes) * CPUS * WALL_H + len(coll) + 0.44,
                "journal_reconciled_lines": sum("reconciled" in l for l in journal), "lock_released": not (R / ".submit.lock").exists()}


R = {}
R["normal_then_duplicate_then_resume"] = scenario([{}, {}, {"mode": "resume"}])
R["reject_at_4_then_resume"] = scenario([{"env": {"FIX_FAIL_AT": "4", "FIX_FAIL_MODE": "reject"}}, {"mode": "resume"}])
R["lost_reply_at_4_then_resume"] = scenario([{"env": {"FIX_FAIL_AT": "4", "FIX_FAIL_MODE": "ambiguous"}}, {"mode": "resume"}])
R["reject_collector_then_resume"] = scenario([{"env": {"FIX_FAIL_AT": "46", "FIX_FAIL_MODE": "reject"}}, {"mode": "resume"}])
R["lost_collector_reply_then_resume"] = scenario([{"env": {"FIX_FAIL_AT": "46", "FIX_FAIL_MODE": "ambiguous"}}, {"mode": "resume"}])
R["reject_at_4_three_finish_then_resume"] = scenario([{"env": {"FIX_FAIL_AT": "4", "FIX_FAIL_MODE": "reject"}}, {"finish": 3, "mode": "resume"}])
R["preflight_refused"] = scenario([{"env": {"FIX_PREFLIGHT_RC": "1"}}])
R["lock_held"] = scenario([{}], prepare=lambda t, R_: (R_.mkdir(parents=True), (R_ / ".submit.lock").mkdir()))
R["resume_with_other_shape"] = scenario([{}, {"mode": "resume", "njobs": 40, "cpus": 9}])
R["resume_without_journal"] = scenario([{"mode": "resume"}])


def ok(r, rcs, calls, nodes, coll, deps=NJOBS, lock=True):
    good = [x["rc"] == 0 for x in r["runs"]] == rcs and [x["qsub_calls"] for x in r["runs"]] == calls and r["node_jobs"] == nodes \
        and r["collectors"] == coll and r["allocated_cpu_hours_bound"] <= CEIL and r["lock_released"] is lock
    if nodes:
        good = good and r["unique_node_names"] == nodes == NJOBS and r["workers_with_one_owner"]
    if coll:
        good = good and r["collector_depends_on"] == deps and r["collector_covers_unfinished_nodes"]
    return good


checks = {
    "normal_then_duplicate_then_resume": ok(R["normal_then_duplicate_then_resume"], [True, False, True], [46, 0, 0], 45, 1),
    "reject_at_4_then_resume": ok(R["reject_at_4_then_resume"], [False, True], [4, 43], 45, 1),
    "lost_reply_at_4_then_resume": ok(R["lost_reply_at_4_then_resume"], [False, True], [4, 42], 45, 1)
        and R["lost_reply_at_4_then_resume"]["journal_reconciled_lines"] == 1,
    "reject_collector_then_resume": ok(R["reject_collector_then_resume"], [False, True], [46, 1], 45, 1),
    "lost_collector_reply_then_resume": ok(R["lost_collector_reply_then_resume"], [False, True], [46, 0], 45, 1)
        and R["lost_collector_reply_then_resume"]["journal_reconciled_lines"] == 1,
    "reject_at_4_three_finish_then_resume": ok(R["reject_at_4_three_finish_then_resume"], [False, True], [4, 43], 45, 1, deps=42),
    "preflight_refused_before_any_qsub": ok(R["preflight_refused"], [False], [0], 0, 0),
    "lock_held_refused": ok(R["lock_held"], [False], [0], 0, 0, lock=False),
    "resume_with_other_shape_refused": ok(R["resume_with_other_shape"], [True, False], [46, 0], 45, 1),
    "resume_without_journal_refused": ok(R["resume_without_journal"], [False], [0], 0, 0),
}
out = {"scope": __doc__, "submit_sha256": __import__("hashlib").sha256(SUBMIT.read_bytes()).hexdigest(), "checks": checks,
       "all_ok": all(checks.values()), "scenarios": R}
(HERE / "s1a_submit_fixture.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps({"checks": checks, "all_ok": out["all_ok"]}, indent=1))
sys.exit(0 if out["all_ok"] else 1)
