"""Stub-scheduler fixtures for s1b_submit.sh (no PBS, no simulation), reusing the s1a_submit_fixture stubs. FIX_BASH selects
the shell; writes s1b_submit_fixture[_FIX_TAG].json beside itself. Keys: a (the wave's job array) and c (the collector)."""
import hashlib, importlib.util, json, os, pathlib, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
SUBMIT = HERE / "s1b_submit.sh"
src = (HERE / "s1a_submit_fixture.py").read_text()
STUBS = {}
exec(src[src.index("STUBS = {"):src.index("\n\n\ndef scenario")], {}, ns := {}) or STUBS.update(ns["STUBS"])
STUBS["python"] = r'''
import json, os, sys
open(os.environ["FIX_PY_CALLS"], "a").write(json.dumps(sys.argv[1:]) + "\n")
print('{"preflight": "%s"}' % ("passed" if os.environ.get("FIX_PREFLIGHT_RC", "0") == "0" else "refused"))
sys.exit(int(os.environ.get("FIX_PREFLIGHT_RC", "0")))
'''
STUBS["python"] = STUBS["python"].replace('import json, os, sys\n', '''import json, os, pathlib, sys
if os.environ.get("FIX_RAISE_LOAD"):                  # live load rises while preflight runs
    pathlib.Path(os.environ["FIX_LOAD_FILE"]).write_text(os.environ["FIX_RAISE_LOAD"])
''', 1)
STUBS["qstat"] = r'''
import json, os, pathlib, sys
st = pathlib.Path(os.environ["FIX_STATE"]); jobs = json.loads(st.read_text()) if st.exists() else []
a = sys.argv[1:]; fail = os.environ.get("FIX_QSTAT_FAIL", "")
if "-u" in a:                                   # the user listing: unfinished jobs and subjobs, minus FIX_HIDE, plus FIX_LOAD_FILE CPUs
    me = a[a.index("-u") + 1]; hide = os.environ.get("FIX_HIDE", "").split(",")
    lf = pathlib.Path(os.environ.get("FIX_LOAD_FILE", "/nonexistent")); load = int(lf.read_text()) if lf.exists() else 0
    print("Job ID          Username Queue    Jobname    SessID NDS TSK Memory Time  S Time")
    print("--------------- -------- -------- ---------- ------ --- --- ------ ----- - -----")
    if load:
        print(f"777777.kunanyi- {me}  normal   other         --    1 {load}   10gb 48:00 R   -- ")
    for j in jobs:
        if j["state"] == "F" or j["id"] in hide:
            continue
        ar = j["args"]
        if "-J" in ar:
            n = int(ar[ar.index("-J") + 1].split("-")[1]) + 1
            cpus = int([x for x in ar if "ncpus=" in x][0].split("ncpus=")[1].split(":")[0])
            print(f"{j['id'][:6]}[].ku {me}  normal   {j['name'][:10]}    --    1 {cpus}   10gb 48:00 B   -- ")
            for i in range(n):
                print(f"{j['id'][:6]}[{i}].ku {me}  normal   {j['name'][:10]}    --    1 {cpus}   10gb 48:00 {j['state']}   -- ")
        else:
            print(f"{j['id'][:15]} {me}  normal   {j['name'][:10]}    --    1 1   16gb 08:00 {j['state']}   -- ")
    sys.exit(0)
jobs = {j["id"]: j for j in jobs}; jid = a[-1]
if "-x" in a and (fail == "all" or jid.split(".")[0] in [str(900000 + int(i)) for i in fail.split(",") if i]):
    print("qstat: cannot connect to server (stub)", file=sys.stderr); sys.exit(2)
j = jobs.get(jid)
if j is None:
    print(f"qstat: Unknown Job Id {jid}", file=sys.stderr); sys.exit(153)
if "-x" in a:
    print(f"Job Id: {jid}\n    Job_Name = {j['name']}\n    job_state = {j['state']}")
elif "-f" in a:
    print("    Mail_Users = fixture\n    Mail_Points = ae")
'''
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
                    FIX_LEDGER=str(t / "ledger.jsonl"), FIX_CALLS=str(t / "calls.jsonl"), FIX_QSELECT_CALLS=str(t / "qselect.n"),
                    FIX_PY_CALLS=str(t / "py.jsonl"), FIX_LOAD_FILE=str(t / "load.txt"), PBS_USER="fixture")
        R = vb / "s1b/run/submit_W1"; J = R / "submit_journal.tsv"
        if step0 := steps[0].get("ledger_locked"):
            (vb / "s1b/.ledger.lock").mkdir()
        ledger = lambda: [json.loads(x) for x in (t / "ledger.jsonl").read_text().splitlines()] if (t / "ledger.jsonl").exists() else []
        runs = []
        for step in steps:
            if "finish" in step or "expire" in step:
                jobs = json.loads((t / "jobs.json").read_text())
                for i in step.get("finish", []):
                    jobs[i]["state"] = "F"
                jobs = [j for k, j in enumerate(jobs) if k not in step.get("expire", [])]
                (t / "jobs.json").write_text(json.dumps(jobs))
            if "load" in step:
                (t / "load.txt").write_text(str(step["load"]))
            if "settings" in step:
                (vb / "s1b/p3_settings.json").write_text(step["settings"])
            for line in step.get("operator", []):
                J.open("a").write(line.format(**{f"id{k}": j["id"] for k, j in enumerate(ledger())},
                                              **{"name_a": next((l.split()[2] for l in J.read_text().splitlines() if l.split()[1] == "a"), "")}) + "\n")
            env = dict(base, **step.get("env", {}))
            before = len((t / "calls.jsonl").read_text().splitlines()) if (t / "calls.jsonl").exists() else 0
            pyb = len((t / "py.jsonl").read_text().splitlines()) if (t / "py.jsonl").exists() else 0
            args = [os.environ.get("FIX_BASH", "bash"), str(SUBMIT), str(vb), "p3_settings.json", "run", "W1", str(NJOBS), str(CPUS),
                    "48:00:00"] + (step["mode"].split() if step.get("mode") else [])
            p = subprocess.run(args, env=env, capture_output=True, text=True)
            after = len((t / "calls.jsonl").read_text().splitlines()) if (t / "calls.jsonl").exists() else 0
            py = [json.loads(x)[2] for x in (t / "py.jsonl").read_text().splitlines()[pyb:]] if (t / "py.jsonl").exists() else []
            runs.append({"mode": step.get("mode", "new"), "rc": p.returncode, "qsub_calls": after - before, "runner_calls": py,
                         "stderr": [l.replace(td, "<tmp>") for l in p.stderr.strip().splitlines()[-1:]]})
        led = ledger(); arrays = [j for j in led if j["name"].endswith("_a")]; coll = [j for j in led if j["name"].endswith("_c")]
        deps = []
        if coll:
            a = coll[0]["args"]; deps = a[a.index("-W") + 1].split(":", 1)[1].split(":") if "-W" in a else []
        jflag = [j["args"][j["args"].index("-J") + 1] for j in arrays]
        tags = [a["args"][a["args"].index("-v") + 1].split("TAG=")[1].split(",")[0] for a in arrays + coll]
        return {"runs": runs, "arrays_created": len(arrays), "array_ranges": jflag, "collectors_created": len(coll), "tags": tags,
                "array_names": [a["name"] for a in arrays], "topup_logs": (R.parent / "submit_W1_b" / "logs").is_dir(),
                "collector_depends_on": deps, "array_ids": [j["id"] for j in arrays],
                "allocated_cpu_hours_bound": len(arrays) * NJOBS * CPUS * WALL_H + len(coll) * 8 + PRIOR,
                "lock_released": not (R / ".submit.lock").exists() and not (vb / "s1b/.ledger.lock").exists()}


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
    "campaign_ledger_lock_held": scenario([{"ledger_locked": True}]),
    "topup_without_seeded_wave": scenario([{"mode": "topup b"}]),
    "new_then_topup_then_duplicate_then_resume": scenario([{}, {"finish": [0, 1], "mode": "topup b"}, {"mode": "topup b"},
                                                           {"mode": "resume b"}]),
    "topup_label_rules": scenario([{}, {"mode": "topup"}, {"mode": "topup B-1"}, {"mode": "new x"}]),
    "topup_with_other_settings_digest": scenario([{}, {"settings": '{"fixture": "other"}', "mode": "topup b"}]),
    "capacity_refused_before_preflight": scenario([{"load": 2840}, {"load": 2839}]),
    "capacity_rechecked_before_request": scenario([{"env": {"FIX_RAISE_LOAD": "2840"}}, {"load": 0}]),
    "accepted_array_unlisted_refuses_topup": scenario([{}, {"env": {"FIX_HIDE": "900000.fixture"}, "mode": "topup b"},
                                                       {"finish": [0, 1], "env": {"FIX_HIDE": "900000.fixture"}, "mode": "topup b"}]),
    "rejected_array_rechecked_on_resume": scenario([fail(1, "reject"), {"operator": ["rejected a {name_a} manual: tracejob shows no job"],
                                                    "load": 2900, "mode": "resume"}, {"load": 0, "mode": "resume"}]),
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
    "campaign_ledger_lock_refuses_concurrent_submission": ok(R["campaign_ledger_lock_held"], [False], [0], 0, 0, lock=False),
    "topup_refused_without_seeded_wave": [x["rc"] == 0 for x in R["topup_without_seeded_wave"]["runs"]] == [False]
        and R["topup_without_seeded_wave"]["runs"][0]["qsub_calls"] == 0 and not R["topup_without_seeded_wave"]["runs"][0]["runner_calls"],
    "topup_adds_array_and_collector_without_seeding": (lambda r: [x["rc"] == 0 for x in r["runs"]] == [True, True, False, True]
        and [x["qsub_calls"] for x in r["runs"]] == [2, 2, 0, 0] and r["runs"][0]["runner_calls"] == ["preflight", "seed"]
        and r["runs"][1]["runner_calls"] == ["preflight"] and r["tags"] == ["W1", "W1_b", "W1", "W1_b"]
        and len(set(r["array_names"])) == 2 and r["topup_logs"] and r["lock_released"])(R["new_then_topup_then_duplicate_then_resume"]),
    "topup_label_rules": [x["rc"] == 0 for x in R["topup_label_rules"]["runs"]] == [True, False, False, False]
        and [x["qsub_calls"] for x in R["topup_label_rules"]["runs"]] == [2, 0, 0, 0],
    "topup_refused_for_another_settings_digest": [x["rc"] == 0 for x in R["topup_with_other_settings_digest"]["runs"]] == [True, False]
        and [x["qsub_calls"] for x in R["topup_with_other_settings_digest"]["runs"]] == [2, 0]
        and not R["topup_with_other_settings_digest"]["runs"][1]["runner_calls"]
        and "differ from the wave's seeded" in R["topup_with_other_settings_digest"]["runs"][1]["stderr"][0],
    "capacity_refused_before_preflight": (lambda r: [x["rc"] == 0 for x in r["runs"]] == [False, True]
        and [x["qsub_calls"] for x in r["runs"]] == [0, 2] and r["runs"][0]["runner_calls"] == []
        and "capacity: 2840 live + 4161 new CPUs exceed 7000" in r["runs"][0]["stderr"][0])(R["capacity_refused_before_preflight"]),
    "capacity_rechecked_before_request": (lambda r: [x["rc"] == 0 for x in r["runs"]] == [False, True]
        and [x["qsub_calls"] for x in r["runs"]] == [0, 2] and r["runs"][0]["runner_calls"] == ["preflight", "seed"]
        and "capacity: 2840 live" in r["runs"][0]["stderr"][0])(R["capacity_rechecked_before_request"]),
    "accepted_array_unlisted_refuses_topup": (lambda r: [x["rc"] == 0 for x in r["runs"]] == [True, False, True]
        and [x["qsub_calls"] for x in r["runs"]] == [2, 0, 2] and r["runs"][1]["runner_calls"] == []
        and "not yet in the live listing: 900000.fixture" in r["runs"][1]["stderr"][0])(R["accepted_array_unlisted_refuses_topup"]),
    "rejected_array_rechecked_on_resume": (lambda r: [x["rc"] == 0 for x in r["runs"]] == [False, False, True]
        and [x["qsub_calls"] for x in r["runs"]] == [1, 0, 2] and "capacity: 2900 live" in r["runs"][1]["stderr"][0])(
        R["rejected_array_rechecked_on_resume"]),
}
bv = subprocess.run([os.environ.get("FIX_BASH", "bash"), "-c", "echo $BASH_VERSION"], capture_output=True, text=True).stdout.strip()
out = {"scope": __doc__, "bash_version": bv, "submit_sha256": hashlib.sha256(SUBMIT.read_bytes()).hexdigest(), "checks": checks,
       "all_ok": all(checks.values()), "scenarios": R}
tag = os.environ.get("FIX_TAG", "")
(HERE / f"s1b_submit_fixture{('_' + tag) if tag else ''}.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps({"bash_version": bv, "checks": checks, "all_ok": out["all_ok"]}, indent=1))
sys.exit(0 if out["all_ok"] else 1)
