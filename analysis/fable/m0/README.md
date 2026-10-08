# Fable M0 generator (independent implementation, v0)

Python/numpy implementation of protocol draft 0.3 §3.1–3.2:
- M0, plus the M_A, M_D (linear, accelerating, step) and M_O (low-n and uniform
  detection) alternatives;
- census schedules with propagation through missing years;
- documented-interpolation replication;
- exact matched selection S.

Written from the protocol text without reading Astra's `analysis/astra/m0/`.
It was frozen (committed) before any comparison.

Run the tests from the repo root:

    ~/.local/bin/uv run --with numpy python analysis/fable/m0/test_sampler.py

Saved output: [test_output.txt](test_output.txt) (19/19 pass).

Not included: priors, calibration banks, validation draws or any empirical
p-value.
