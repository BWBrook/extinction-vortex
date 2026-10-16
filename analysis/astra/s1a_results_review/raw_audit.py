"""Audit saved Stage 1a outputs on deep-server without any new simulation.

Run through Python stdin on deep-server. Reads the fetched tar, extracted
files and accepted source; reruns collection into an audit-owned directory.
No PBS command, model fit, bank scan or sampling entry point is invoked.
"""
from collections import Counter
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import resource
import subprocess
import tarfile
import time
from zoneinfo import ZoneInfo

ROOT = Path('/data/fable/vortex')
P2 = ROOT / 'v2_dev/p2'
BASE = P2 / 's1a_main'
RUN = BASE / 'main'
SRC = ROOT / 'kunanyi_stage/run1/src'
OUT = Path('/data/codex/artifacts/project/s1a_results_review')
OUT.mkdir(parents=True, exist_ok=True)
START = time.monotonic()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(p):
    return json.loads(p.read_text())


settings_path = BASE / 'p2_settings_s1a.json'
metric_path = BASE / 'p2_metric.json'
settings = read(settings_path)
binding = dict(settings_sha256=sha(settings_path.read_bytes()),
               metric_sha256=sha(metric_path.read_bytes()),
               runner_sha256=sha((ROOT / 'v2_dev/p2_stage1a.py').read_bytes()))
assert binding['settings_sha256'] == '6018ed2a56fa5d778728dc6c1ddd72fb4959c2959475cd153e093616029546f2'
assert binding['metric_sha256'] == settings['metric_sha256']
assert binding['runner_sha256'] == settings['runner_sha256']
assert sha((ROOT / 'v2_dev/p1_sampler.py').read_bytes()) == settings['p1_sampler_sha256']
for name, digest in settings['imported_source_sha256'].items():
    assert sha((SRC / name).read_bytes()) == digest
tar_path = BASE / 'main.tar.gz'
members = {}
with tarfile.open(tar_path) as tf:
    for m in tf:
        name = m.name.removeprefix('./')
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        if not m.isfile():
            assert m.isdir()
            continue
        assert name not in members
        raw = tf.extractfile(m).read()
        digest = sha(raw)
        assert digest == sha((BASE / name).read_bytes()), name
        members[name] = digest
assert 'main/collect.json' in members
original = read(RUN / 'collect.json')
saved_deep = read(BASE / 'collect_deep.json')
assert original == saved_deep
assert sha(tar_path.read_bytes()).startswith('3e18e5b8')

command = ['/usr/bin/python3', '-I', str(ROOT / 'v2_dev/p2_stage1a.py'), 'collect',
           str(settings_path), str(metric_path), str(RUN), str(OUT / 'collect_astra.json')]
env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', FLEXIBLAS_NUM_THREADS='1')
proc = subprocess.run(command, cwd=SRC, env=env, capture_output=True, text=True, timeout=120)
assert proc.returncode == 0, proc.stderr
new = read(OUT / 'collect_astra.json')
assert new == original
assert new['binding'] == binding and new['collection_ok'] and new['provenance_complete']
assert not new['run_complete'] and new['n_errors'] == 0 and not new['workers_missing']
rows = new['rows']
assert [r['index'] for r in rows] == list(range(1080))
assert sorted(w['worker'] for w in new['workers']) == list(range(360))

prefix_matches = 0
prefix_hits = 0
for st, r in zip(settings['settings'], rows):
    assert all(r[k] == st[k] for k in ('index', 'pop', 'outer', 'n', 'worker', 'proposal_budget'))
    assert r['uncommitted_tail_bytes'] == 0
    if r['proposals'] >= 100000:
        hp = RUN / f"s{r['index']:04d}_hits.jsonl"
        raw = hp.read_bytes() if hp.exists() else b''
        lines = raw.splitlines(keepends=True)
        prefix = b''.join(line for line in lines if json.loads(line)['batch'] < 5)
        old = P2 / 'dry3' / hp.name
        assert prefix == (old.read_bytes() if old.exists() else b'')
        assert len(prefix.splitlines()) == r['prefix_hits']
        prefix_matches += 1
        prefix_hits += r['prefix_hits']

journal = [line.split() for line in (RUN / 'submit_journal.tsv').read_text().splitlines()]
counts = Counter(line[0] for line in journal)
assert counts == {'request': 46, 'accepted': 46}
accepted = {line[1]: line[3] for line in journal if line[0] == 'accepted'}
assert len(accepted) == 46 and len(set(accepted.values())) == 46
assert set(accepted) == {f'j{i}' for i in range(45)} | {'c'}
node_ids = (RUN / 'node_jobs.txt').read_text().splitlines()
assert node_ids == [accepted[f'j{i}'] for i in range(45)]
assert (RUN / 'collect_job.txt').read_text().strip() == accepted['c']
pfraw = (RUN / 'logs/preflight.log').read_text()
pf, fixtures = pfraw.split('\n', 1)
preflight = json.loads(pf)
assert preflight['preflight'] == 'passed' and not preflight['errors']
assert preflight['settings_sha256'] == binding['settings_sha256']
assert preflight['allocated_cpu_hours_bound'] == 991.445 and json.loads(fixtures)['all_ok']
jobs = []
for line in (RUN / 'logs/jobs.log').read_text().splitlines():
    m = re.fullmatch(r'job (\d+) host (\S+) workers failed: (\d+)', line)
    assert m, line
    j, host, failed = m.groups()
    assert failed == '0'
    jobs.append(int(j))
assert sorted(jobs) == list(range(45))
exposure = {k: sum(r[k] for r in rows) for k in ('proposals', 'paths', 'selected_SA', 'hits', 'boundary', 'cpu_seconds')}
wall = Counter()
for r in rows:
    wall[r['worker']] += r['wall_seconds']
proxy = sum(8 * max(wall[w] for w in range(j*8, (j+1)*8)) for j in range(45)) / 3600
result = dict(timestamp=datetime.now(ZoneInfo('Australia/Hobart')).isoformat(), scope=__doc__,
              host=platform.node(), python=platform.python_version(), binding=binding,
              archive_sha256=sha(tar_path.read_bytes()), archive_bytes=tar_path.stat().st_size,
              archive_regular_files_verified=len(members), archive_member_manifest_sha256=sha(json.dumps(members, sort_keys=True).encode()),
              archived_collect_sha256=members['main/collect.json'], saved_deep_collect_sha256=sha((BASE / 'collect_deep.json').read_bytes()),
              collector_command=command, collector_returncode=proc.returncode, collector_stdout=proc.stdout,
              collector_stderr=proc.stderr, all_collections_identical=True, status=new['status'], exposure=exposure,
              prefix_settings_matched=prefix_matches, prefix_hits_matched=prefix_hits,
              workers=len(new['workers']), hosts=len({w['host'] for w in new['workers']}),
              max_rss_gib=max(w['peak_rss_gib'] for w in new['workers']),
              no_exposure=[r['index'] for r in rows if r['proposals']==0],
              censored=[r['index'] for r in rows if r['status']=='censored'],
              journal_counts=dict(counts), accepted_jobs=accepted, node_worker_logs_all_zero=True,
              preflight=preflight, run_identity=(RUN / 'run.json').read_text().strip(),
              node_allocation_lower_proxy_cpu_h=proxy,
              accounting_limit='No PBS resources_used.walltime receipt read; proxy excludes setup and collector. Submission bound is 991.445 allocated CPU-hours.',
              elapsed_seconds=time.monotonic()-START, collector_peak_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)
(OUT / 'archive_member_hashes.json').write_text(json.dumps(members, indent=2)+'\n')
(OUT / 'raw_audit.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
