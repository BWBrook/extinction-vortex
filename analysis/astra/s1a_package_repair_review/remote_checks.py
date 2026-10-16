"""Read-only repair-package audit on deep-server; no sampler, bank load or scheduler call.

Run through stdin with Python 3. Reads the staged tar in place and compares the
fourth saved smoke with the original archived run. Earlier metric/input findings
are reused only after checking unchanged byte hashes in the local companion.
"""
from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path
import platform
import tarfile
import time
from zoneinfo import ZoneInfo

ROOT = Path('/data/fable/vortex')
P2 = ROOT / 'v2_dev/p2'
SRC = ROOT / 'kunanyi_stage/run1/src'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads(path.read_text())


def main():
    started = time.monotonic()
    settings = read(P2 / 'p2_settings_s1a.json')
    smoke = read(P2 / 'p2_settings_smoke3.json')
    actual = {
        'runner': digest((ROOT / 'v2_dev/p2_stage1a.py').read_bytes()),
        'helper': digest((ROOT / 'v2_dev/p1_sampler.py').read_bytes()),
        'metric': digest((P2 / 'p2_metric.json').read_bytes()),
        'settings': digest((P2 / 'p2_settings_s1a.json').read_bytes()),
        'throughput': digest((P2 / 'throughput_kunanyi.json').read_bytes()),
        'smoke_settings': digest((P2 / 'p2_settings_smoke3.json').read_bytes()),
    }
    for key, field in [('runner', 'runner_sha256'), ('helper', 'p1_sampler_sha256'),
                       ('metric', 'metric_sha256'), ('throughput', 'throughput_sha256')]:
        assert actual[key] == settings[field]
    imported = {p: digest((SRC / p).read_bytes()) for p in settings['imported_source_sha256']}
    assert imported == settings['imported_source_sha256']
    tar_path = P2 / 's1a_stage_final.tar'
    with tarfile.open(tar_path) as tf:
        members = {m.name.removeprefix('./'): digest(tf.extractfile(m).read())
                   for m in tf.getmembers() if m.isfile()}
        manifest = tf.extractfile('./s1a/stage_sha256.txt').read().decode()
    listed = {}
    for line in manifest.splitlines():
        sha, path = line.split(maxsplit=1)
        listed[path.removeprefix('./')] = sha
    assert len(listed) == 8
    assert all(members[p] == h for p, h in listed.items())
    assert set(members) == set(listed) | {'s1a/stage_sha256.txt'}
    binding = {'settings_sha256': actual['smoke_settings'], 'metric_sha256': actual['metric'],
               'runner_sha256': actual['runner']}
    collect = read(P2 / 'dry3/collect.json')
    assert collect['binding'] == binding
    assert collect['collection_ok'] and collect['run_complete'] and collect['n_errors'] == 0
    assert collect['status'] == dict(complete=1080, censored=0, failed=0, running=0, missing=0, invalid=0)
    assert [r['index'] for r in collect['rows']] == list(range(1080))
    assert sorted(w['worker'] for w in collect['workers']) == list(range(28))
    assert all(w['nworkers'] == 28 and w['binding'] == binding for w in collect['workers'])
    counters = ('proposals', 'poisson_accept', 'theta_accept', 'paths', 'selected_SA',
                'overflow', 'hits', 'boundary', 'hits_lo', 'hits_hi', 'rounding_excess',
                'batches_done')
    totals = Counter()
    journal_bytes = 0
    for i, st in enumerate(smoke['settings']):
        assert st['index'] == i and st['proposal_budget'] == 100000 and st['batches'] == 5
        original = read(P2 / 'dry' / f's{i:04d}.json')
        new = read(P2 / 'dry3' / f's{i:04d}.json')
        assert new['binding'] == binding and new['status'] == original['status'] == 'complete'
        assert all(new[k] == original[k] == collect['rows'][i][k] for k in counters)
        paths = [P2 / name / f's{i:04d}_hits.jsonl' for name in ('dry', 'dry3')]
        journals = [p.read_bytes() if p.exists() else b'' for p in paths]
        assert journals[0] == journals[1]
        assert len(journals[1].splitlines()) == new['hits']
        assert new['journal_bytes'] == len(journals[1])
        assert new['journal_sha256'] == digest(journals[1])
        journal_bytes += len(journals[1])
        totals.update({k: new[k] for k in counters})
    print(json.dumps({
        'timestamp': datetime.now(ZoneInfo('Australia/Hobart')).isoformat(),
        'scope': __doc__, 'python': platform.python_version(),
        'actual_hashes': actual, 'imported_source_hashes': imported,
        'stage_tar_sha256': digest(tar_path.read_bytes()), 'stage_tar_bytes': tar_path.stat().st_size,
        'stage_listed_hashes': listed, 'stage_manifest_sha256': members['s1a/stage_sha256.txt'],
        'stage_manifest_matches_all_eight_files': True,
        'dry3_collect_sha256': digest((P2 / 'dry3/collect.json').read_bytes()),
        'dry3_settings_and_checkpoints_bound': 1080, 'dry3_workers_bound': 28,
        'dry3_matches_original_counters_and_journal_bytes': 1080,
        'dry3_journal_bytes': journal_bytes, 'dry3_totals': dict(totals),
        'elapsed_seconds': time.monotonic() - started,
    }, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
