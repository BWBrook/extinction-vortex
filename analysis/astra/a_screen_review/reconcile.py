"""Reconcile remote audit JSON against local archives; retain a compressed receipt."""
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
PEER = ROOT/'analysis/fable/calibration/v2_dev/a_screen'
OUT = Path(__file__).with_name('raw_audit.json.gz')


def main(path):
    j = json.loads(Path(path).read_text())
    for name,h in j['small_input_sha256'].items():
        assert hashlib.sha256((PEER/name).read_bytes()).hexdigest() == h, name
    manifest = {n:h for h,n in (line.split() for line in
                               (PEER/'T_and_neighbour_sha256.txt').read_text().splitlines())}
    remote = '/data/fable/vortex/v2_dev/a_screen/'
    hashes = {n.removeprefix(remote):h for n,h in j['T_sha256'].items()
              if n.startswith(remote)} | j['neighbour_sha256']
    assert manifest == hashes
    for n,h in j['runner_sha256'].items():
        assert hashlib.sha256((PEER.parent/Path(n).name).read_bytes()).hexdigest() == h, n
    previous = json.loads(gzip.decompress((ROOT/'analysis/astra/validation_v1_audit/raw_score.json.gz').read_bytes()))
    old = previous['archive']['member_sha256']
    base = '/data/fable/vortex/kunanyi_run1/extract/'
    baseline = {n:h for n,h in j['T_sha256'].items() if n.startswith(base)}
    assert len(baseline) == 200
    for n,h in baseline.items():
        assert old[n.removeprefix(base)] == h, n
    j['local_archive_reconciliation'] = {
        'compact_files_matched':len(j['small_input_sha256']),
        'manifest_entries_matched':len(manifest),
        'all_four_retained_runner_dependencies_match':True,
        'baseline_T_files_match_sealed_v1_audit':len(baseline)}
    OUT.write_bytes(gzip.compress(json.dumps(j,indent=2).encode(),mtime=0))
    print(json.dumps(j['local_archive_reconciliation']))


if __name__ == '__main__':
    main(sys.argv[1])
