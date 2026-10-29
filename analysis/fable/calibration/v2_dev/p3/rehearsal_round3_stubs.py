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
led.open("a").write(json.dumps(job) + "\n")
if n == at and mode == "ambiguous_expired":
    sys.exit(1)
jobs.append(job); st.write_text(json.dumps(jobs))
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
