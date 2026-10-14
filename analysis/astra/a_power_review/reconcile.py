"""Match the remote audit to committed compact files and the sealed v1 receipt."""
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
PEER = ROOT/'analysis/fable/calibration/v2_dev/a_power'


def main(path):
    receipt = json.loads(Path(path).read_text())
    for name, digest in receipt['small_input_sha256'].items():
        assert hashlib.sha256((PEER/name).read_bytes()).hexdigest() == digest, name
    manifest = {name: digest for digest, name in
                (line.split() for line in (PEER/'T_and_neighbour_sha256.txt').read_text().splitlines())}
    prefix = '/data/fable/vortex/v2_dev/a_power/'
    current = {name.removeprefix(prefix): digest for name, digest in receipt['T_sha256'].items()
               if name.startswith(prefix)} | receipt['neighbour_sha256']
    assert len(manifest) == 602 and manifest == current
    for name, digest in receipt['helper_sha256'].items():
        assert hashlib.sha256((PEER.parent/name).read_bytes()).hexdigest() == digest, name
    previous = json.loads(gzip.decompress(
        (ROOT/'analysis/astra/validation_v1_audit/raw_score.json.gz').read_bytes()))
    old = previous['archive']['member_sha256']
    base = '/data/fable/vortex/kunanyi_run1/extract/'
    baseline = {name.removeprefix(base): digest for name, digest in receipt['T_sha256'].items()
                if name.startswith(base)}
    assert len(baseline) == 600
    for name, digest in baseline.items():
        assert old[name] == digest, name
    receipt['local_archive_reconciliation'] = {
        'compact_files_matched': len(receipt['small_input_sha256']),
        'manifest_entries_matched': len(manifest),
        'retained_helpers_matched': len(receipt['helper_sha256']),
        'baseline_T_files_match_sealed_v1_audit': len(baseline)}
    Path(__file__).with_name('raw_audit.json.gz').write_bytes(
        gzip.compress(json.dumps(receipt, indent=2, allow_nan=False).encode(), mtime=0))
    print(json.dumps(receipt['local_archive_reconciliation']))


if __name__ == '__main__':
    main(sys.argv[1])
