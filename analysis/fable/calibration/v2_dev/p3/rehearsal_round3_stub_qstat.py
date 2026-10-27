#!/usr/bin/python3
"""Stub qstat for the round-3 dispatch rehearsal: jobs from FIX_STATE (written by the stub qsub, each with a state);
the eight round-2 jobs answer job_state F except FIX_NOT_F; arrays report array_state_count; unknown IDs exit 153."""
import json, os, sys
a = sys.argv[1:]; jobs = json.load(open(os.environ["FIX_STATE"]))
R2 = {"857922[]", "857923", "858016[]", "858017", "860989[]", "860990", "860992[]", "860993"}


def size(j):
    ar = j["args"]
    return (int(ar[ar.index("-J") + 1].split("-")[1]) + 1 if "-J" in ar else 0,
            int([x for x in ar if "ncpus=" in x][0].split("ncpus=")[1].split(":")[0]) if any("ncpus=" in x for x in ar) else 1)


if "-u" in a:
    me = a[a.index("-u") + 1]
    print("\nkunanyi-ohpc:\n                                                            Req'd  Req'd   Elap")
    print("Job ID          Username Queue    Jobname    SessID NDS TSK Memory Time  S Time")
    print("--------------- -------- -------- ---------- ------ --- --- ------ ----- - -----")
    for j in jobs:
        if j["state"] == "F":
            continue
        n, cpus = size(j)
        if n:
            print(f"{j['id'][:8]}[].kun {me}  normal   {j['name'][:10]}    --    1   {cpus}   10gb 48:00 B   -- ")
            for i in range(n):
                print(f"{j['id'][:6]}[{i}].ku {me}  normal   {j['name'][:10]}    --    1   {cpus}   10gb 48:00 {j['state']}   -- ")
        else:
            print(f"{j['id'][:15]} {me}  normal   {j['name'][:10]}    --    1   1   16gb 08:00 {j['state']}   -- ")
    sys.exit(0)
jid = a[-1]
if jid in R2:
    print(f"Job Id: {jid}\n    job_state = {'R' if jid == os.environ.get('FIX_NOT_F') else 'F'}"); sys.exit(0)
j = {x["id"]: x for x in jobs}.get(jid)
if j is None or (j["state"] == "F" and "-x" not in a):
    print(f"qstat: Unknown Job Id {jid}", file=sys.stderr); sys.exit(153)
n, _ = size(j)
print(f"Job Id: {jid}\n    Job_Name = {j['name']}\n    job_state = {'B' if n and j['state'] != 'F' else j['state']}")
if n:
    live = 0 if j["state"] == "F" else n
    print(f"    array_state_count = Queued:{live} Running:0 Exiting:0 Expired:{n - live}")
print(f"    Mail_Users = fixture\n    Mail_Points = ae\n    depend = afterany:{jid}")
