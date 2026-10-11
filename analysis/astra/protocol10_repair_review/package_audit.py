"""Check the repaired freeze's identities and unchanged scientific settings; no compute."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
F = ROOT / 'analysis/fable/calibration/freeze_v1'
CODE = '52779d0'
EXPECTED = '96603037ec05036153f67b649757d067ca193c5e0a8610d3b855ef8f22139429'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def historical(name):
    return json.loads(subprocess.check_output(['git', 'show', '9578156:analysis/fable/calibration/freeze_v1/' + name], cwd=ROOT))


def main():
    manifest = F / 'validation_manifest.json'
    man = json.loads(manifest.read_text())
    assert sha(manifest) == EXPECTED
    old = historical('validation_manifest.json')
    for field in ('variant', 'R', 'K', 'budget', 'beta_min'):
        assert man[field] == old[field]
    old_scenarios = old['scenarios']
    for s in old_scenarios:
        for c in s['chunks']:
            c['dir'] = c['dir'].replace('/data/fable/vortex/', '')
    assert man['scenarios'] == old_scenarios
    stress = json.loads((F / 'stress_sets.json').read_text())
    previous = historical('stress_sets.json')
    assert stress['sets'] == previous['sets'] and stress['seed'] == previous['seed']
    assert sha(F / 'stress_sets.json') == man['stress_sets_sha256']
    assert sha(F / 'effect_target_ar_cat.json') == man['effect_sha256']
    old_inputs = {Path(p).name: h for h, p in
                  (line.split(maxsplit=1) for line in (F / 'package_inputs_sha256.txt').read_text().splitlines())}
    assert stress['library_sha256'] == old_inputs['libraries_ar_cat.npz']
    source = {}
    for path, digest in man['source_sha256'].items():
        got = sha(ROOT / path)
        at_commit = hashlib.sha256(subprocess.check_output(['git', 'show', CODE + ':' + path], cwd=ROOT)).hexdigest()
        assert got == digest == at_commit
        source[path] = digest
    shard_hashes = {Path(path).name: digest for digest, path in
                    (line.split(maxsplit=1) for line in (F / 'bank_primary_sha256.txt').read_text().splitlines())}
    assert len(shard_hashes) == 180
    assert {k: v for k, v in man['bank_sha256'].items() if k.endswith('.npz')} == shard_hashes
    assert man['bank_sha256']['bank_meta.json'] == sha(F / 'bank_primary_meta.json')
    preflight = json.loads((F / ('preflight_' + EXPECTED[:16] + '.json')).read_text())
    assert preflight['manifest_digest'] == EXPECTED
    assert preflight['checked_source'] == 12 and preflight['checked_bank_shards'] == 181
    assert all(preflight['runtime'][k] == v for k, v in man['runtime_pins'].items())
    stale = {p: {'old': digest, 'current': sha(F / p)} for p, digest in old_inputs.items()
             if (F / p).exists() and digest != sha(F / p)}
    result = {'reviewed_code': subprocess.check_output(['git', 'rev-parse', CODE], cwd=ROOT, text=True).strip(),
              'manifest_digest': EXPECTED, 'unchanged_settings': ['variant','R','K','budget','beta_min','all scenarios, chunks, IDs and seeds'],
              'unchanged_stress_vectors': 2700, 'source_hashes': source,
              'bank_shard_hashes_matching_previous_independent_audit': 180,
              'bank_metadata_hash_matches': True, 'preflight_receipt': preflight,
              'stale_legacy_package_input_receipt_entries': stale,
              'limits': ['No rerun of scientific simulations, R fits or full bank hashing.',
                         'Hash continuity relies on the earlier raw-bank audit in protocol10_review/evidence_check.json.',
                         'Effect JSON is hashed in the manifest; preflight does not read it because execution uses embedded parameters.']}
    out = Path(__file__).with_suffix('.json')
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'source_hashes'}, indent=2))


if __name__ == '__main__':
    main()
