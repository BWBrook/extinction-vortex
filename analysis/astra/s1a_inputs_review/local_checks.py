"""Reconcile remote Stage 1a audit with committed inputs and earlier receipts.
Also rerun the earlier tiny Stage 0 report fixtures with the repaired hash
contract's expected outcome. No raw bank or simulator is loaded locally.
"""
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
V2=ROOT/'analysis/fable/calibration/v2_dev'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    remote=json.loads((HERE/'remote_checks.json').read_text())
    checks={}
    for key,path in [('metric_sha256',V2/'p2/p2_metric.json'),('settings_sha256',V2/'p2/p2_settings_s1a.json'),('runner_sha256',V2/'p2_stage1a.py')]:
        checks[key]=sha(path)==remote[key]
    for p in ['kunanyi_smoke/collect.json']:
        checks[p]=sha(V2/'p2'/p)==remote['smoke_archives']['kunanyi']['collect_sha256']
    old=json.loads((ROOT/'analysis/astra/stage0_info_review/remote_audit.json').read_text())
    checks['all_nine_raw_s0_match_previous_audit']=all(old['raw_sha256'][f's0_{p}.json']==h for p,h in remote['raw_s0_sha256'].items())
    assert all(checks.values())
    # Retain the earlier fixture file unchanged. Only its expected disposition
    # for a wrong runner hash changes from accepted to rejected in this replay.
    fixture=ROOT/'analysis/astra/p1_cost_and_guard_review/checks.py'
    source=fixture.read_text()
    old_expected="(case in ('valid','wrong_runner_hash'))"
    assert source.count(old_expected)==1
    ns={'__name__':'prior_fixture_replay','__file__':str(fixture)}
    exec(compile(source.replace(old_expected,"(case == 'valid')"),str(fixture),'exec'),ns)
    guard=ns['guard_fixtures']()
    assert not guard['report_cases']['wrong_runner_hash']['accepted']
    guard.pop('remaining_guard')  # This sentence describes the old defect, now closed.
    result=dict(timestamp=datetime.now(ZoneInfo('Australia/Hobart')).isoformat(),
                checked_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                remote_receipt_sha256=sha(HERE/'remote_checks.json'),reconciled=checks,
                prior_fixture_sha256=sha(fixture),fixture_expected_change='wrong_runner_hash must now be rejected',
                stage0_guard_fixtures=guard,stage0_runner_binding_finding_closed=True,
                caribou_minor_changes='Read diff 36cf1a6..e3870d4: both same-surveys phrases replaced by shared monitoring programme; blank line before A11 removed. No new figure or data change.')
    (HERE/'local_checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
