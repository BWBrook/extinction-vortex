"""Match the 18 November printed claim hints to per-setting death counts at collection."""

from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys


receipt, summary = (Path(p).read_bytes() for p in sys.argv[1:])
assert hashlib.sha256(receipt).hexdigest() == "ce367971ed080ea63c5fea7e5dafe1f3b74c0a048a42da6158205badcc37fa76"
assert hashlib.sha256(summary).hexdigest() == "fc376cd2d741ed4fdf6283607a198f6f8158ceecd8bcd7e8b3906e6ed403acbb"
body = receipt.decode()
jobs = re.search(r"^\s*jobs = (.+)$", body, re.MULTILINE).group(1).split(", ")
slots = Counter(job.split(".")[0] for job in jobs)
assert sorted(int(job.rsplit("/", 1)[1]) for job in jobs) == list(range(28))
assert slots["876193[22]"] == slots["876193[23]"] == 8
assert all(re.search(rf"^-- 876193\[{sub}\]:  job_state = F  substate = 91\b", body, re.MULTILINE)
           for sub in (22, 23))
claims = re.findall(r"^W2_\d+_([sc]\d+)_(\d+)_(\d+)@(876193\[2[23]\]\.[^\s]+)$", body, re.MULTILINE)
total = int(re.search(r"^count: (\d+)$", body, re.MULTILINE).group(1))
assert total == 32 and len(claims) == len(set(claims)) == 20
shown = Counter(c[0] for c in claims)
rows = {r["dir"]: r for r in json.loads(summary)["rows"]}
cells = {d: {"shown_hints": n, "all_snapshot_dead_ends": rows[d]["dead_executions"]} for d, n in sorted(shown.items())}
possible = sum(min(n, rows[d]["dead_executions"]) for d, n in shown.items())
print(json.dumps({"slots_before_deletion": {"876193[22]": 8, "876193[23]": 8, "other": len(jobs) - 16},
                  "both_post_deletion_states_F_91": True, "total_claim_hints": total,
                  "shown_hints": len(claims), "by_setting": cells,
                  "shown_hints_in_settings_with_zero_snapshot_dead_ends": sum(n for d, n in shown.items()
                                                                               if rows[d]["dead_executions"] == 0),
                  "maximum_distinct_snapshot_dead_ends_matching_shown_hints": possible,
                  "maximum_of_32_claim_hints_that_can_match_snapshot_dead_ends": possible + total - len(claims)},
                 indent=2))
