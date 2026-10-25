#!/usr/bin/python3
import json, os, sys
a = sys.argv[1:]; jobs = json.load(open(os.environ["FIX_STATE"]))
if "-u" in a:
    me = a[a.index("-u") + 1]
    print("\nkunanyi-ohpc:\n                                                            Req'd  Req'd   Elap")
    print("Job ID          Username Queue    Jobname    SessID NDS TSK Memory Time  S Time")
    print("--------------- -------- -------- ---------- ------ --- --- ------ ----- - -----")
    if os.environ.get("FIX_CASE") != "badcount":
        print(f"858016[].kunany {me}  normal   s1b_3a5e71    --    1   8   10gb 48:00 B   -- ")
        for i in range(379):
            print(f"858016[{i}].kuna {me}  normal   s1b_3a5e71 1234   1   8   10gb 48:00 R 20:00")
        print(f"858017.kunanyi- {me}  normal   s1b_3a5e71    --    1   1   16gb 08:00 H   -- ")
    for j in jobs:
        ar = j["args"]
        if "-J" in ar:
            n = int(ar[ar.index("-J") + 1].split("-")[1]) + 1
            cpus = int([x for x in ar if "ncpus=" in x][0].split("ncpus=")[1].split(":")[0])
            print(f"{j['id'][:8]}[].kun {me}  normal   {j['name'][:10]}    --    1   {cpus}   10gb 48:00 Q   -- ")
            for i in range(n):
                print(f"{j['id'][:6]}[{i}].ku {me}  normal   {j['name'][:10]}    --    1   {cpus}   10gb 48:00 Q   -- ")
        else:
            print(f"{j['id'][:15]} {me}  normal   {j['name'][:10]}    --    1   1   16gb 08:00 H   -- ")
    sys.exit(0)
jid = a[-1]
if jid == "858016[]":
    print("    job_state = B\n    array_state_count = Queued:0 Running:379 Exiting:0 Expired:191"); sys.exit(0)
if jid in ("857922[]", "857923"):
    print(f"Job Id: {jid}\n    job_state = F"); sys.exit(0)
j = {x["id"]: x for x in jobs}.get(jid)
if j is None:
    print(f"qstat: Unknown Job Id {jid}", file=sys.stderr); sys.exit(153)
if "-x" in a:
    print(f"Job Id: {jid}\n    job_state = {j['state']}")
else:
    print(f"    Mail_Users = fixture\n    Mail_Points = ae\n    depend = afterany:{jid}")
