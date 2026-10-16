"""Stub-scheduler fixtures for s1a_submit.sh (no PBS, no simulation). Writes s1a_submit_fixture.json beside itself.
Each scenario runs the real script in a fresh directory with stub qsub/qselect/qstat (PBS_BIN) and a stub preflight
(S1A_ENV). qsub can reject (no job) or accept but lose its reply (job created, non-zero exit) at a chosen call; qselect
can fail at a chosen call; qstat -x can fail for chosen jobs; finished jobs can be expired from history. Every job ever
created is kept in an append-only ledger, so allocation and worker ownership are counted even after history expiry."""
import hashlib, json, os, pathlib, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
SUBMIT = HERE / "s1a_submit.sh"
NJOBS, CPUS, WALL_H, CEIL, PRIOR = 45, 8, 2.75, 1000.0, 0.445
STUBS = {
    "qsub": r'''
import json, os, pathlib, sys
st, led, calls = (pathlib.Path(os.environ[k]) for k in ("FIX_STATE", "FIX_LEDGER", "FIX_CALLS"))
jobs = json.loads(st.read_text()) if st.exists() else []
n = (len(calls.read_text().splitlines()) if calls.exists() else 0) + 1
calls.open("a").write(json.dumps(sys.argv[1:]) + "\n")
a = sys.argv[1:]; at, mode = int(os.environ.get("FIX_FAIL_AT", "-1")), os.environ.get("FIX_FAIL_MODE", "")
if n == at and mode == "reject":
    sys.exit(7)
jid = f"{900000 + (len(led.read_text().splitlines()) if led.exists() else 0)}.fixture"
job = {"id": jid, "name": a[a.index("-N") + 1], "args": a, "state": "Q"}
jobs.append(job); st.write_text(json.dumps(jobs)); led.open("a").write(json.dumps(job) + "\n")
if n == at and mode == "ambiguous":
    sys.exit(1)
print(jid)
''',
    "qselect": r'''
import json, os, pathlib, sys
st, calls = pathlib.Path(os.environ["FIX_STATE"]), pathlib.Path(os.environ["FIX_QSELECT_CALLS"])
n = (int(calls.read_text()) if calls.exists() else 0) + 1; calls.write_text(str(n))
if n == int(os.environ.get("FIX_QSELECT_FAIL_AT", "-1")):
    print("qselect: cannot connect to server (stub)", file=sys.stderr); sys.exit(2)
jobs = json.loads(st.read_text()) if st.exists() else []
a = sys.argv[1:]; name = a[a.index("-N") + 1]
for j in jobs:
    if j["name"] == name and ("-x" in a or j["state"] != "F"):
        print(j["id"])
''',
    "qstat": r'''
import json, os, pathlib, sys
jobs = {j["id"]: j for j in json.loads(pathlib.Path(os.environ["FIX_STATE"]).read_text())}
a = sys.argv[1:]; jid = a[-1]; fail = os.environ.get("FIX_QSTAT_FAIL", "")
if "-x" in a and (fail == "all" or jid.split(".")[0] in [str(900000 + int(i)) for i in fail.split(",") if i]):
    print("qstat: cannot connect to server (stub)", file=sys.stderr); sys.exit(2)
j = jobs.get(jid)
if j is None:
    print(f"qstat: Unknown Job Id {jid}", file=sys.stderr); sys.exit(153)
if "-x" in a:
    print(f"Job Id: {jid}\n    Job_Name = {j['name']}\n    job_state = {j['state']}")
elif "-f" in a:
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
        base = dict(os.environ, PBS_BIN=str(fb), S1A_ENV=str(envf), S1A_CONFIRM_SECS="0", FIX_STATE=str(t / "jobs.json"),
                    FIX_LEDGER=str(t / "ledger.jsonl"), FIX_CALLS=str(t / "calls.jsonl"), FIX_QSELECT_CALLS=str(t / "qselect.n"))
        R = vb / "s1a/main"; J = R / "submit_journal.tsv"
        if prepare:
            prepare(t, R)
        ledger = lambda: [json.loads(x) for x in (t / "ledger.jsonl").read_text().splitlines()] if (t / "ledger.jsonl").exists() else []
        runs = []
        for step in steps:
            if "finish" in step or "expire" in step:
                jobs = json.loads((t / "jobs.json").read_text())
                for i in step.get("finish", []):
                    jobs[i]["state"] = "F"
                jobs = [j for k, j in enumerate(jobs) if k not in step.get("expire", [])]
                (t / "jobs.json").write_text(json.dumps(jobs))
            for kind, key, idx, evidence in step.get("operator", []):        # an operator's verified journal entry
                job = ledger()[idx] if idx is not None else None
                name = job["name"] if job else next(l.split()[2] for l in J.read_text().splitlines() if l.split()[1] == key)
                line = {"accepted": f"accepted {key} {name} {job and job['id']} manual: {evidence}",
                        "rejected": f"rejected {key} {name} manual: {evidence}",
                        "terminal": f"terminal {key} {job and job['id']} manual: {evidence}"}[kind]
                J.open("a").write(line + "\n")
            if step.get("only_operator"):
                continue
            env = dict(base, **step.get("env", {}))
            before = len((t / "calls.jsonl").read_text().splitlines()) if (t / "calls.jsonl").exists() else 0
            args = ["bash", str(SUBMIT), str(vb), "settings.json", "main", str(step.get("njobs", NJOBS)), str(step.get("cpus", CPUS)),
                    "02:45:00", str(CEIL), str(PRIOR)] + ([step["mode"]] if step.get("mode") else [])
            p = subprocess.run(args, env=env, capture_output=True, text=True)
            after = len((t / "calls.jsonl").read_text().splitlines()) if (t / "calls.jsonl").exists() else 0
            runs.append({"mode": step.get("mode", "new"), "rc": p.returncode, "qsub_calls": after - before,
                         "stderr": [l.replace(td, "<tmp>") for l in p.stderr.strip().splitlines()[-1:]]})
        led = ledger(); nodes = [j for j in led if "_j" in j["name"]]; coll = [j for j in led if j["name"].endswith("_c")]
        owners = []
        for j in nodes:
            v = dict(x.split("=", 1) for x in j["args"][j["args"].index("-v") + 1].split(","))
            owners += range(int(v["JOB"]) * int(v["JOBCPUS"]), (int(v["JOB"]) + 1) * int(v["JOBCPUS"]))
        deps = []
        if coll:
            a = coll[0]["args"]
            deps = a[a.index("-W") + 1].split(":", 1)[1].split(":") if "-W" in a else []
        journal = J.read_text().splitlines() if J.exists() else []
        return {"runs": runs, "node_jobs_created": len(nodes), "unique_node_names": len({j["name"] for j in nodes}),
                "collectors_created": len(coll), "workers_each_owned_once": sorted(owners) == list(range(NJOBS * CPUS)),
                "collector_depends_on": len(deps), "allocated_cpu_hours_bound": len(nodes) * CPUS * WALL_H + len(coll) + PRIOR,
                "journal_tail": journal[-3:], "lock_released": not (R / ".submit.lock").exists()}


def ok(r, rcs, calls, nodes, coll, deps=NJOBS, lock=True):
    good = [x["rc"] == 0 for x in r["runs"]] == rcs and [x["qsub_calls"] for x in r["runs"]] == calls \
        and r["node_jobs_created"] == nodes and r["collectors_created"] == coll \
        and r["allocated_cpu_hours_bound"] <= CEIL and r["lock_released"] is lock
    if nodes == NJOBS:
        good = good and r["unique_node_names"] == NJOBS and r["workers_each_owned_once"]
    if coll:
        good = good and r["collector_depends_on"] == deps
    return good


fail = lambda at, mode, **kw: {"env": dict({"FIX_FAIL_AT": str(at), "FIX_FAIL_MODE": mode}, **kw)}
R = {}
R["normal_then_duplicate_then_resume"] = scenario([{}, {}, {"mode": "resume"}])
R["reject_at_4_then_resume"] = scenario([fail(4, "reject"), {"mode": "resume"}])
R["lost_reply_at_4_reconciled_at_once"] = scenario([fail(4, "ambiguous")])
# qselect calls: lookups for j0..j3 are calls 1-4; the confirmation after the failed qsub for j3 is call 5
R["lost_reply_unconfirmed_history_expired"] = scenario([
    fail(4, "ambiguous", FIX_QSELECT_FAIL_AT="5"), {"finish": [3], "expire": [3], "mode": "resume"},
    {"operator": [("accepted", "j3", 3, "accounting log shows the job ran"),
                  ("terminal", "j3", 3, "accounting log shows it finished")], "mode": "resume"}])
R["reject_unconfirmed_then_operator_rejects"] = scenario([
    fail(4, "reject", FIX_QSELECT_FAIL_AT="5"), {"mode": "resume"},
    {"operator": [("rejected", "j3", None, "tracejob shows no such job")], "mode": "resume"}])
R["collector_rejected_then_resume"] = scenario([fail(46, "reject"), {"mode": "resume"}])
R["collector_reply_lost_reconciled_at_once"] = scenario([fail(46, "ambiguous")])
R["three_finished_before_collector"] = scenario([fail(4, "reject"), {"finish": [0, 1, 2], "mode": "resume"}])
R["one_live_query_fails_then_resume"] = scenario([{"env": {"FIX_QSTAT_FAIL": "5"}}, {"mode": "resume"}])
R["all_queries_fail_then_resume"] = scenario([{"env": {"FIX_QSTAT_FAIL": "all"}}, {"mode": "resume"}])
R["finished_job_history_expired_then_terminal"] = scenario([
    fail(46, "reject"), {"finish": [0], "expire": [0], "mode": "resume"},
    {"operator": [("terminal", "j0", 0, "job0.out and jobs.log show completion")], "mode": "resume"}])
R["preflight_refused"] = scenario([{"env": {"FIX_PREFLIGHT_RC": "1"}}])
R["lock_held"] = scenario([{}], prepare=lambda t, R_: (R_.mkdir(parents=True), (R_ / ".submit.lock").mkdir()))
R["resume_with_other_shape"] = scenario([{}, {"mode": "resume", "njobs": 40, "cpus": 9}])
R["resume_without_journal"] = scenario([{"mode": "resume"}])

checks = {
    "normal_then_duplicate_then_resume": ok(R["normal_then_duplicate_then_resume"], [True, False, True], [46, 0, 0], 45, 1),
    "reject_at_4_then_resume": ok(R["reject_at_4_then_resume"], [False, True], [4, 43], 45, 1),
    "lost_reply_at_4_reconciled_at_once": ok(R["lost_reply_at_4_reconciled_at_once"], [True], [46], 45, 1),
    "lost_reply_unconfirmed_history_expired_no_replacement": ok(
        R["lost_reply_unconfirmed_history_expired"], [False, False, True], [4, 0, 42], 45, 1, deps=44),
    "reject_unconfirmed_then_operator_rejects": ok(R["reject_unconfirmed_then_operator_rejects"], [False, False, True], [4, 0, 43], 45, 1),
    "collector_rejected_then_resume": ok(R["collector_rejected_then_resume"], [False, True], [46, 1], 45, 1),
    "collector_reply_lost_reconciled_at_once": ok(R["collector_reply_lost_reconciled_at_once"], [True], [46], 45, 1),
    "three_finished_before_collector": ok(R["three_finished_before_collector"], [False, True], [4, 43], 45, 1, deps=42),
    "one_live_query_fails_no_collector_then_resume": ok(R["one_live_query_fails_then_resume"], [False, True], [45, 1], 45, 1),
    "all_queries_fail_no_collector_then_resume": ok(R["all_queries_fail_then_resume"], [False, True], [45, 1], 45, 1),
    "finished_job_history_expired_then_terminal": ok(
        R["finished_job_history_expired_then_terminal"], [False, False, True], [46, 0, 1], 45, 1, deps=44),
    "preflight_refused_before_any_qsub": ok(R["preflight_refused"], [False], [0], 0, 0),
    "lock_held_refused": ok(R["lock_held"], [False], [0], 0, 0, lock=False),
    "resume_with_other_shape_refused": ok(R["resume_with_other_shape"], [True, False], [46, 0], 45, 1),
    "resume_without_journal_refused": ok(R["resume_without_journal"], [False], [0], 0, 0),
}
out = {"scope": __doc__, "submit_sha256": hashlib.sha256(SUBMIT.read_bytes()).hexdigest(), "checks": checks,
       "all_ok": all(checks.values()), "scenarios": R}
(HERE / "s1a_submit_fixture.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps({"checks": checks, "all_ok": out["all_ok"]}, indent=1))
sys.exit(0 if out["all_ok"] else 1)
