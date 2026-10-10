"""Reconcile the 0.8 archive to Astra's existing raw-statistic audit; no simulations.

Run from the repository root with python3. Writes evidence_check.json beside this file.
The remote T files were read in the earlier audit, not fetched or fitted again here.
"""
import hashlib
import json
import math
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).with_suffix('.json')
POWER = ROOT / 'analysis/fable/calibration/power_screen_v1'
AUDIT = ROOT / 'analysis/astra/protocol08_precheck/power_screen_audit.json'
old = json.loads(AUDIT.read_text())
hashes = {r['path']: r['sha256'] for r in old['manifest']}
local_hashes = {}
for arm in old['summary']:
    for filename in ('e2e_meta.json', 'e2e_rows.jsonl'):
        rel = f'{arm}/{filename}'
        got = hashlib.sha256((POWER / rel).read_bytes()).hexdigest()
        assert got == hashes[rel], rel
        local_hashes[rel] = got

manifest = {}
for line in (POWER / 'T_sha256.txt').read_text().splitlines():
    digest, filename = line.split(maxsplit=1)
    # Fable records relative paths including the arm; normalize leading ./ only.
    manifest[filename.removeprefix('./')] = digest
expected_t = {k: v for k, v in hashes.items() if k.endswith('.csv')}
assert manifest == expected_t, 'raw T manifest differs from earlier independent audit'

scored = json.loads((POWER / 'scored_summary.json').read_text())
outcomes = {}
for arm, earlier in old['summary'].items():
    rows = [json.loads(line) for line in (POWER / arm / 'e2e_rows.jsonl').read_text().splitlines()]
    assert [r['outer'] for r in rows] == list(range(30))
    counts = dict(Counter(r['outcome'] for r in rows))
    assert counts == earlier['outcomes']
    assert scored[arm]['reject'] == earlier['rejections']
    assert scored[arm]['accept'] + scored[arm]['reject'] == 30
    assert scored[arm]['missing'] == 0
    outcomes[arm] = counts

resources = (POWER / 'resources.txt').read_text()
cpu = sum(float(re.search(rf'{kind} time \(seconds\):\s*([\d.]+)', resources).group(1))
          for kind in ('User', 'System'))
per_trial = cpu / 150 / 3600
cost = {label: count * per_trial for label, count in
        [('null_4000', 4000), ('alternatives_3000', 3000),
         ('detection_curve_600', 600), ('predictive_stress_300', 300)]}
cost['empirical_placeholder'] = 5
cost['banks_placeholder'] = 120
cost['total_core_hours'] = sum(cost.values())

# Mathematical diagnostic of the proposed retained-theta sampler's finite retry cap.
# These are examples, NOT measured selection rates for the empirical libraries.
cap = 1_000_000
retry = [{'p_selection': p, 'p_success_by_cap': -math.expm1(cap * math.log1p(-p))}
         for p in (1e-5, 1e-6, 1e-7)]

inputs = [AUDIT, POWER / 'T_sha256.txt', POWER / 'scored_summary.json', POWER / 'resources.txt']
result = {
    'reviewed_commit': subprocess.check_output(['git', 'rev-parse', 'f8546ec'], cwd=ROOT, text=True).strip(),
    'scope': 'Archive identity, fixed trial counts, cost arithmetic and analytic retry-cap examples only.',
    'local_archive_files_matching_prior_audit': local_hashes,
    'T_manifest_entries_matching_prior_raw_audit': len(manifest),
    'outcomes': outcomes,
    'cpu_seconds': cpu,
    'core_hours_per_trial': per_trial,
    'cost_inventory': cost,
    'projected_7900_trial_hours_at_prior_observed_throughput':
        7900 / old['throughput_planning']['post_load_datasets_per_hour'],
    'retry_cap': {'draws_per_theta': cap, 'examples': retry,
                  'completed_theta_weight': 'q(theta) proportional to 1-(1-p_selection(theta))^M'},
    'input_hashes': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
    'limitations': ['No new raw T file retrieval or refitting.',
                    'No independent replay of bank generation or coverage arrays.',
                    'Sensitivity subtotal is a placeholder, not a complete section 7 execution manifest.',
                    'Retry probabilities are hypothetical analytic examples, not measured library frequencies.'],
}
OUT.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'matched_T_hashes': len(manifest), 'matched_local_files': len(local_hashes),
                  'outcomes': outcomes, 'cost': cost, 'retry_cap_examples': retry}, indent=2))
