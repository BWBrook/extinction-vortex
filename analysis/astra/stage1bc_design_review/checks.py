"""Bounded stream-map, inventory and gate arithmetic. No trajectories or fits."""
import json
from pathlib import Path

from scipy.stats import beta, binom


def settings(ntrial):
    return [(p, s, t, n) for p in range(9) for s in range(4)
            for t in range(ntrial) for n in (0, 30, 300)]


def gates(n):
    # Preserve v1's four-null-cell family and original power confidence rule.
    null_ok = [k for k in range(n + 1)
               if (beta.ppf(.9875, k+1, n-k) if k < n else 1) <= .08]
    power_ok = [k for k in range(n + 1)
                if (beta.ppf(.05, k, n-k+1) if k else 0) >= .70]
    k = max(null_ok) if null_ok else None
    return dict(n=n, null_max_nonaccepts=k, power_min_detections=min(power_ok),
                null_upper_bound_at_zero=float(beta.ppf(.9875, 1, n)),
                null_pass_probability_if_true_nonaccept_rate_005=
                    float(binom.cdf(k, n, .05)) if k is not None else 0)


old, naive = settings(10), settings(200)
new_index = {x: i for i, x in enumerate(naive)}
result = {
    "scope": "Design implications only; naive extension is not an implemented Stage1b bug",
    "stream_mapping": {
        "pilot_settings": len(old), "full_settings": len(naive),
        "pilot_ids_changed_by_naive_loop_extension": sum(new_index[x] != i for i, x in enumerate(old)),
        "example_seed_id": 30,
        "old_target_pop_scenario_trial_n": old[30],
        "naive_new_target_pop_scenario_trial_n": naive[30],
    },
    "inventory": {
        "informative_population_libraries": 9*4*200*2,
        "shared_n0_population_libraries": 9*4*200,
        "total_primary_population_libraries": 9*4*200*3,
        "primary_retained_pairs_K2000": 9*4*200*3*2000,
        "informative_analyses": 4*200*2,
        "shared_n0_analyses": 4*200,
        "total_primary_analyses": 4*200*3,
        "nominal_T_vector_evaluations_4001_each": 4*200*3*4001,
        "example_second_library_check_2_outers_per_scenario_all_n": {
            "analyses": 4*2*3, "population_libraries": 4*2*3*9,
            "retained_pairs": 4*2*3*9*2000,
            "nominal_T_vector_evaluations": 4*2*3*4001,
        },
    },
    "gates": [gates(n) for n in (25, 50, 200, 300, 1000)],
}
assert result["gates"][2]["null_max_nonaccepts"] == 7
assert result["gates"][2]["power_min_detections"] == 152
assert result["gates"][3]["power_min_detections"] == 224
assert result["gates"][4]["null_max_nonaccepts"] == 60
Path(__file__).with_name("checks.json").write_text(json.dumps(result, indent=2)+"\n")
print(json.dumps(result, indent=2))
