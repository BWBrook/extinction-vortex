"""Deterministic checks of the proposed informative-reference law, not a sampler.

Run with a Python environment containing NumPy and SciPy:
  python checks.py OUTPUT.json
No population paths, random draws, likelihood fits or bank reads.
"""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from scipy.special import xlogy, xlog1py
from scipy.stats import binom, poisson


def log_kernel(u, v, n, k, r):
    return xlogy(k, u) + xlog1py(n-k, -u) + xlogy(r, v) - n*v


def envelope(n, k, r):
    return log_kernel(k/n, r/n, n, k, r)


def normalize(values):
    return [v / sum(values) for v in values]


def main(output):
    noisy_cases = 0
    largest_excess = -float('inf')
    full_pmf_max_error = 0.0
    factor_max_error = 0.0
    for n in (1, 30, 300):
        for k in sorted({0, n//2, n}):
            for r in (0, 1, 3, 2*n):
                H = envelope(n, k, r)
                H_full = binom.logpmf(k, n, k/n) + poisson.logpmf(r, r)
                for u in (0.0, 0.0001, 0.2, 0.5, 0.9, 0.9999, 1.0):
                    for v in (0.0, 0.0001, 0.01, 0.1, 1.0, 2.0):
                        h = log_kernel(u, v, n, k, r)
                        log_accept = h-H
                        largest_excess = max(largest_excess, log_accept)
                        assert log_accept <= 1e-10
                        full = binom.logpmf(k, n, u) + poisson.logpmf(r, n*v) - H_full
                        if np.isfinite(log_accept):
                            full_pmf_max_error = max(full_pmf_max_error, abs(full-log_accept))
                            assert abs(full-log_accept) < 2e-10
                        else:
                            assert np.isneginf(full)
                        hs = xlogy(k, u) + xlog1py(n-k, -u)
                        Hs = xlogy(k, k/n) + xlog1py(n-k, -k/n)
                        hf = xlogy(r, v) - n*v
                        Hf = xlogy(r, r/n) - r
                        factor_max_error = max(factor_max_error,
                            abs(np.exp(log_accept) - np.exp(hs-Hs)*np.exp(hf-Hf)))
                        noisy_cases += 1
    ideal_cases = 0
    for n in (30, 300):
        for u0, v0 in ((0.0, 0.0), (0.17, 0.035), (0.48, 0.32), (1.0, 2.0)):
            k, r = n*u0, n*v0
            H = envelope(n, k, r)
            assert abs(log_kernel(u0, v0, n, k, r)-H) < 1e-10
            for u in (0.0, 0.1, 0.3, 0.7, 1.0):
                for v in (0.0, 0.01, 0.3, 1.0, 2.0):
                    assert log_kernel(u, v, n, k, r)-H <= 1e-10
                    ideal_cases += 1

    # Two nuisance states, then selection and a conditional C-neighbourhood.
    pi, likelihood = [F(1, 2), F(1, 2)], [F(1, 5), F(4, 5)]
    selection, c_given_selection = [F(1, 10), F(9, 10)], [F(4, 5), F(1, 5)]
    target = normalize([pi[i]*likelihood[i]*selection[i]*c_given_selection[i]
                        for i in range(2)])
    posterior_E = normalize([pi[i]*likelihood[i] for i in range(2)])
    proposed = normalize([posterior_E[i]*selection[i]*c_given_selection[i]
                          for i in range(2)])
    wrong_hold_theta = normalize([posterior_E[i]*c_given_selection[i] for i in range(2)])
    q = [F(4, 5), F(1, 5)]
    weighted = normalize([q[i]*selection[i]*c_given_selection[i] * pi[i]*likelihood[i]/q[i]
                          for i in range(2)])
    assert target == proposed == weighted == [F(1, 10), F(9, 10)]
    assert wrong_hold_theta == [F(1, 2), F(1, 2)]
    root = Path(__file__).resolve().parents[3]
    proposal = root/'notes/astra_informative_reference_proposal_20261014.md'
    receipt = {
        'scope': 'Deterministic envelope and finite probability identities only; no sampler or compute benchmark',
        'noisy_envelope_cases': noisy_cases, 'largest_log_acceptance_excess': largest_excess,
        'normalized_kernel_vs_full_pmf_max_error': full_pmf_max_error,
        'factorized_vs_joint_acceptance_max_error': factor_max_error,
        'ideal_fractional_cases': ideal_cases,
        'joint_selection_example': {'target': list(map(str, target)),
            'evidence_then_one_path': list(map(str, proposed)),
            'fixed_q_importance_weights': list(map(str, weighted)),
            'incorrect_hold_theta_until_selected': list(map(str, wrong_hold_theta))},
        'limits': 'Finite numerical examples supplement the analytic concavity bound; no acceptance efficiency, path-wrapper equivalence or statistical calibration measured.',
        'proposal_sha256_at_check': hashlib.sha256(proposal.read_bytes()).hexdigest(),
    }
    Path(output).write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main(sys.argv[1])
