"""Small exact probability checks; no population simulation or fitted model."""
import json
import math
from pathlib import Path


def stopped_bernoulli(p, target, batch, max_batches):
    # Exact finite-state recursion for batched Bernoulli inverse sampling.
    active = {0: 1.0}
    terminal = []
    pmf = [math.comb(batch, j) * p**j * (1-p)**(batch-j)
           for j in range(batch+1)]
    for b in range(1, max_batches+1):
        nxt = {}
        for old_h, mass in active.items():
            for j, prob in enumerate(pmf):
                h = old_h+j
                z = mass*prob
                if h >= target or b == max_batches:
                    terminal.append((b*batch, h, z, h >= target))
                else:
                    nxt[h] = nxt.get(h, 0.0)+z
        active = nxt
    mass = sum(z for _, _, z, _ in terminal)
    complete_mass = sum(z for _, _, z, hit in terminal if hit)
    assert abs(mass-1) < 1e-12
    return {
        "p": p, "target": target, "batch": batch,
        "proposal_cap": batch*max_batches,
        "probability_reaching_target": complete_mass,
        "mean_H_over_N_all_outcomes": sum(h/n*z for n,h,z,_ in terminal),
        "mean_H_over_N_conditional_on_target_reached":
            sum(h/n*z for n,h,z,hit in terminal if hit)/complete_mass,
        "maximum_retained_count": max(h for _,h,_,_ in terminal),
    }


result = {
    "scope": "Exact small Bernoulli examples, not estimates for Stage 1a.",
    "ideal_unbatched_uncensored_K2000_relative_bias_upper_bound": 1/1999,
    "ideal_unbatched_uncensored_K2000_approx_relative_standard_error_rare_p":
        1/math.sqrt(2000),
    "whole_crossing_batch_strict_record_bound": 2000+20000-1,
    "zero_hit_rule3_crossing_probability_upper_bound": math.exp(-3),
    "toy_examples": [stopped_bernoulli(p, 20, 4, 25) for p in (0.1, 0.2, 0.4)],
}
Path(__file__).with_name("checks.json").write_text(json.dumps(result, indent=2)+"\n")
print(json.dumps(result, indent=2))
