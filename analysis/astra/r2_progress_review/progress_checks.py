"""Local arithmetic and tiny fixtures for the 23 October live progress probe.

The exact probe function is extracted by AST; it runs only on temporary
synthetic checkpoints. No remote or production paths are accessed.
"""
import ast
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
V2 = ROOT / "analysis/fable/calibration/v2_dev"
PROBE = V2 / "p3/r2_probe.sh"
RECEIPT = V2 / "p3/r2_progress_20261023.txt"
RUNNER = V2 / "p3_stage1b.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract(source, name, env):
    tree = ast.parse(source)
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(compile(ast.Module(body=[node], type_ignores=[]), "<reviewed-source>", "exec"), env)
    return env[name]


def main():
    text = RECEIPT.read_text()
    group_pattern = r"(W[12]) n=(\d+): (\{[^\n]+?\})  worker CPU-h (\d+)  open hit-progress median (\S+) p90 (\S+)"
    groups = []
    for w,n,counts,cpu,median,p90 in re.findall(group_pattern,text):
        groups.append(dict(wave=w,n=int(n),marker_counts=ast.literal_eval(counts),
                           readable_shard_cpu_h_rounded=int(cpu),
                           raw_hit_fraction_median_printed=median,raw_hit_fraction_p90_printed=p90))
    assert len(groups) == 3
    g0,g30,g300 = groups
    assert g0["marker_counts"] == {"COMPLETE":2055}
    assert g30["marker_counts"] == {"COMPLETE":2621,"open":171}
    assert g300["marker_counts"] == {"open":7272}
    pbs = {}
    for w,allocated,cput in re.findall(r"(w[12]) subjobs:.*allocated CPU-h (\d+) cput-h (\d+)",text):
        a,c = int(allocated),int(cput)
        pbs[w.upper()] = dict(reported_allocated_cpu_h=a,reported_cput_h=c,
                              gap_h=a-c,cput_over_allocated=c/a)
    assert pbs["W1"]["gap_h"] == 9795 and pbs["W2"]["gap_h"] == 625

    python_source = PROBE.read_text().split("python -I - <<'PY'\n",1)[1].split("\nPY\n",1)[0]
    fixtures = []
    with tempfile.TemporaryDirectory(prefix="r2-probe-review-") as tmp:
        run = Path(tmp)
        env = dict(json=json,os=os,R=str(run))
        probe = extract(python_source,"one",env)

        def setting(name,pilot=None):
            return dict(dir=name,wave="W1",n=30,pilot=pilot)

        def put(name,filename,value):
            folder=run/"sets"/name; folder.mkdir(parents=True,exist_ok=True)
            (folder/filename).write_text(value if isinstance(value,str) else json.dumps(value))

        put("s_gap","sh000000000.json",dict(status="running",first_batch=0,batches_done=1,hits=0,cpu_seconds=3600))
        put("s_gap","sh000000010.json",dict(status="complete",first_batch=10,batches_done=10,hits=1520,cpu_seconds=7200))
        got=probe(setting("s_gap"))
        prefix_env = dict(K=2000,ranges=lambda _: [(0,10),(10,20)],
                          shard_state=lambda folder,a: json.loads((Path(folder)/f"sh{a:09d}.json").read_text()))
        prefix=extract(RUNNER.read_text(),"prefix",prefix_env)
        contiguous=prefix(setting("s_gap"),str(run/"sets/s_gap"))
        assert got[3] == 1520 and contiguous[1] == 0
        fixtures.append(dict(name="hits_beyond_prefix_hole",probe=got,
                             probe_fraction=got[3]/2000,contiguous_prefix_hits=contiguous[1]))

        put("s_unreadable","sh000000000.json","{invalid JSON")
        got=probe(setting("s_unreadable")); assert got[2:5] == ("open",0,0.)
        fixtures.append(dict(name="unreadable_checkpoint_silently_skipped",probe=got))

        put("s_marker","COMPLETE","{}"); put("s_marker","FAILED","{}")
        got=probe(setting("s_marker")); assert got[2:5] == ("COMPLETE",0,0.)
        fixtures.append(dict(name="complete_marker_no_checkpoints_and_conflicting_failed_marker",probe=got))

        got=probe(setting("s_absent")); assert got[2:5] == ("open",0,0.)
        fixtures.append(dict(name="absent_directory_is_open_zero",probe=got))

        put("s_unbound","sh000000000.json",dict(binding={"wrong":True},status="failed",hits=1800,cpu_seconds=3600))
        got=probe(setting("s_unbound")); assert got[2:5] == ("open",1800,3600.)
        fixtures.append(dict(name="unvalidated_shard_fields_counted",probe=got))

        got=probe(setting("s_pilot",dict(hits=20,cpu_seconds=3600)))
        assert got[3:5] == (20,0.)
        fixtures.append(dict(name="pilot_hits_counted_but_pilot_cpu_excluded",probe=got))

    arithmetic=dict(
        w1_replay_marked_complete=4676,w1_replay_denominator=4847,
        w1_replay_marker_completion_fraction=4676/4847,
        w1_n30_marker_completion_fraction=2621/2792,
        w1_readable_shard_cpu_h_from_rounded_groups=4543+48768,
        raw_shard_cpu_group_sum=4543+48768+18390,raw_shard_cpu_total_printed=71700,
        rounding_note="Group totals were rounded separately; their one-hour difference does not establish an accounting error.",
        historical_w1_complete_plus_current_marker_count=9695+4676,
        historical_w1_capped_retained=2,full_w1_inventory=14544,
        nonzero_exit_log_count=6587+1382,
        certificates_minus_exit_records=8980-1011,
        second_message_type_tally=7931+16+13+5+4+2,
        second_hour_bin_tally=sum([422,24,2954,1536,1391,251,404,288,176,224,225,78]),
        active_subjob_allocated_cores=(291+186)*8,
        w1_delay_slot_hours_if_15_to_20_seconds=[6587*15/3600,6587*20/3600],
        all_delay_slot_hours_if_15_to_20_seconds=[7969*15/3600,7969*20/3600],
        cap_tally_contract="82 slots have >=19 logged nonzero exits; max is20. Exact count reaching20 is not given.",
        cpu_cost_contract="The checkpoint probe excludes imported pilot CPU and omits lost uncommitted CPU and overhead; PBS reports a different scope.")
    out=dict(timestamp=datetime.now(ZoneInfo("Australia/Hobart")).isoformat(),
             target_head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
             source_sha256={str(p.relative_to(ROOT)):sha(p) for p in (PROBE,RECEIPT,RUNNER)},
             groups=groups,pbs_summary_arithmetic=pbs,arithmetic=arithmetic,
             synthetic_fixtures=fixtures,
             scope="Local saved-text arithmetic and exact-function fixtures only; no validation of live production journals or raw PBS records.")
    (HERE/"progress_checks.json").write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(dict(fixture_count=len(fixtures),arithmetic=arithmetic,pbs=pbs),indent=2))


if __name__ == "__main__":
    main()
