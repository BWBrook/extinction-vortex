"""Package the independent raw-score receipt and descriptive v2 diagnostics.

Usage: python3 summarise.py /tmp/project-v1-independent-score.json
No model fitting, simulation, empirical statistic or production scorer import.
"""
import gzip
import hashlib
import json
from pathlib import Path
import statistics
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    raw = Path(sys.argv[1]).read_bytes()
    data = json.loads(raw)
    peer = ROOT / 'analysis/fable/calibration/validation_v1/validation_summary.json'
    assert sha(peer.read_bytes()) == data['summary_sha256']
    provenance = json.loads((HERE / 'provenance_audit.json').read_text())
    assert provenance['pass']
    assert provenance['manifest_sha256'] == data['manifest_sha256']
    for relative, digest in provenance['remote_checks']['input_sha256'].items():
        assert data['archive']['member_sha256']['validation_v1/' + relative] == digest

    compressed = gzip.compress(raw, mtime=0)
    (HERE / 'raw_score.json.gz').write_bytes(compressed)
    summary = {k: data[k] for k in ['method', 'manifest_sha256', 'summary_sha256',
                                   'v_fail', 'fit_stop', 'power_pass', 'wall_seconds', 'limits']}
    summary['raw_score_json_sha256'] = sha(raw)
    summary['raw_score_gzip_sha256'] = sha(compressed)
    summary['archive_sha256'] = data['archive']['archive_sha256']
    summary['matched_archive_members'] = data['archive']['matched_extracted_files']
    summary['provenance_input_hashes_matched'] = len(provenance['remote_checks']['input_sha256'])
    summary['blocks'] = [b['summary'] for b in data['blocks']]
    summary['total_trials'] = sum(b['n'] for b in summary['blocks'])
    summary['total_dataset_vectors'] = sum(b['fitted_datasets'] for b in summary['blocks'])
    summary['failed_dataset_vectors'] = sum(b['failed_datasets'] for b in summary['blocks'])
    summary['diagnostics_status'] = 'Post-hoc description of exposed v1 synthetic outputs; v2 development only.'
    diagnostics = []
    for b in data['blocks'][:4]:
        residuals = list(zip(*(r['marginal_standardized_residual'] for r in b['rows'])))
        diagnostics.append({
            'block': b['summary']['block'], 'name': b['summary']['name'],
            'mean_marginal_standardized_residual_T1_to_T4': [statistics.mean(x) for x in residuals],
            'sd_marginal_standardized_residual_T1_to_T4': [statistics.stdev(x) for x in residuals],
            'median_D_obs': statistics.median(r['D_obs'] for r in b['rows']),
            'max_covariance_condition': max(r['condition'] for r in b['rows']),
            'p_below_0_1': sum(r['p_hi'] < .1 for r in b['rows']),
            'p_below_0_2': sum(r['p_hi'] < .2 for r in b['rows']),
        })
    summary['null_block_diagnostics'] = diagnostics
    (HERE / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({k: summary[k] for k in ['total_trials', 'total_dataset_vectors',
          'failed_dataset_vectors', 'v_fail', 'fit_stop', 'power_pass', 'null_block_diagnostics']}, indent=2))


if __name__ == '__main__':
    main()
