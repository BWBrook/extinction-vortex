#!/usr/bin/env python3
"""Independent local audit of the saved W2 first-array collection snapshot."""

import collections
import hashlib
import importlib.util
import json
import math
import pathlib
import re
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[3]
SUMMARY = ROOT / "analysis/fable/calibration/v2_dev/p3/w2_a_collect_W2.json"
RUNNER = ROOT / "analysis/fable/calibration/v2_dev/p3_stage1b.py"
RECEIPT = ROOT / "analysis/fable/calibration/v2_dev/p3/w2_a_collection_20261027.txt"


def load_runner():
    spec = importlib.util.spec_from_file_location("p3_stage1b_audit", RUNNER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def valid_hit(p3, batch=0, proposal=0):
    return {
        "batch": batch,
        "proposal_in_batch": proposal,
        "boundary": False,
        "theta": {key: 0.1 for key in p3.p2.PARAMS},
        "recorded": [10, 5, 1],
    }


def checkpoint(p3, data, *, status, batches=1, hits=1):
    counters = {key: 0 for key in p3.p2.COUNTERS}
    counters.update(
        proposals=batches * p3.BATCH,
        poisson_accept=hits,
        theta_accept=hits,
        paths=hits,
        selected_SA=hits,
        hits=hits,
        hits_lo=hits,
        hits_hi=hits,
    )
    return {
        "index": 0,
        "binding": {"fixture": "coherent"},
        "status": status,
        "batches_done": batches,
        "cpu_seconds": 1.0,
        "wall_seconds": 1.0,
        "journal_bytes": len(data),
        "journal_sha256": hashlib.sha256(data).hexdigest(),
        **counters,
    }


def expect_error(fn, contains):
    try:
        fn()
    except ValueError as exc:
        return contains in str(exc), str(exc)
    return False, None


def journal_checks(p3):
    line = (json.dumps(valid_hit(p3), separators=(",", ":")) + "\n").encode()
    with tempfile.TemporaryDirectory() as td:
        path = pathlib.Path(td) / "hits.jsonl"

        path.write_bytes(line + line)
        terminal = checkpoint(p3, line, status="complete")
        term_ok, term_error = expect_error(
            lambda: p3.verified(terminal, path, 0, 1, 3, True),
            "journal length differs",
        )

        nonterminal_records = p3.verified(terminal | {"status": "running"}, path, 0, 1, 3, False)

        committed_duplicate = checkpoint(p3, line + line, status="complete", hits=2)
        dup_ok, dup_error = expect_error(
            lambda: p3.verified(committed_duplicate, path, 0, 1, 3, True),
            "duplicated or out of order",
        )

        path.write_bytes(line)
        coherent_unrecomputed = p3.verified(terminal, path, 0, 1, 3, True)

    return {
        "terminal_uncommitted_duplicate_tail_rejected": term_ok,
        "terminal_tail_error": term_error,
        "nonterminal_duplicate_tail_excluded": len(nonterminal_records) == 1,
        "nonterminal_verified_records": len(nonterminal_records),
        "committed_duplicate_identity_rejected": dup_ok,
        "committed_duplicate_error": dup_error,
        "coherent_structural_record_not_recomputed": len(coherent_unrecomputed) == 1,
    }


def main():
    summary = json.loads(SUMMARY.read_text())
    rows = summary["rows"]
    status = collections.Counter(row["status"] for row in rows)
    library_status = collections.defaultdict(lambda: {"n": 0, "useful_cpu_h": 0.0, "discarded_cpu_h": 0.0})
    for row in rows:
        key = f"{row['status']}|{row['library']}"
        library_status[key]["n"] += 1
        library_status[key]["useful_cpu_h"] += row.get("useful_cpu_h", 0.0)
        library_status[key]["discarded_cpu_h"] += row.get("discarded_cpu_h", 0.0)

    inventory = collections.Counter()
    outcomes = collections.Counter()
    for row in rows:
        scenario = row["outer"].split("/")[0]
        key = (row["library"], row["pop"], scenario)
        inventory[key] += 1
        outcomes[(row["status"], *key)] += 1
    primary_cells = [n for (library, _, _), n in inventory.items() if library == "primary"]
    check_cells = [n for (library, _, _), n in inventory.items() if library == "check"]
    complete_primary_by_outer = collections.Counter(
        row["outer"] for row in rows if row["library"] == "primary" and row["status"] == "COMPLETE"
    )

    accounted_useful = sum(row.get("useful_cpu_h", 0.0) for row in rows)
    accounted_discarded = sum(row.get("discarded_cpu_h", 0.0) for row in rows)
    incomplete_discarded = sum(
        row.get("discarded_cpu_h", 0.0) for row in rows if row["status"] == "incomplete"
    )
    invalid = [row["dir"] for row in rows if row["status"] == "invalid"]
    recheck_terminals = collections.Counter(
        match.group(2)
        for line in RECEIPT.read_text().splitlines()
        if (match := re.match(r"^([sc]\d+) terminal (FAILED|None|COMPLETE) \|", line))
    )

    result = {
        "inputs": {
            "summary": str(SUMMARY.relative_to(ROOT)),
            "summary_sha256": hashlib.sha256(SUMMARY.read_bytes()).hexdigest(),
            "runner": str(RUNNER.relative_to(ROOT)),
            "runner_sha256": hashlib.sha256(RUNNER.read_bytes()).hexdigest(),
            "receipt": str(RECEIPT.relative_to(ROOT)),
        },
        "summary_contract": {
            "rows": len(rows),
            "status_recomputed": dict(status),
            "status_saved": summary["status"],
            "errors": len(summary["errors"]),
            "invalid_rows": len(invalid),
            "error_dirs_equal_invalid_dirs": sorted(x.split(":", 1)[0] for x in summary["errors"]) == sorted(invalid),
            "collection_ok": summary["collection_ok"],
            "invalid_recheck_terminal_markers": dict(recheck_terminals),
        },
        "fixed_denominators": {
            "primary_rows": sum(row["library"] == "primary" for row in rows),
            "check_rows": sum(row["library"] == "check" for row in rows),
            "primary_cells": len(primary_cells),
            "primary_rows_per_population_scenario": sorted(set(primary_cells)),
            "check_cells": len(check_cells),
            "check_rows_per_population_scenario": sorted(set(check_cells)),
            "primary_complete": sum(row["library"] == "primary" and row["status"] == "COMPLETE" for row in rows),
            "check_complete": sum(row["library"] == "check" and row["status"] == "COMPLETE" for row in rows),
            "outer_datasets_with_all_9_primary_libraries_complete": sum(n == 9 for n in complete_primary_by_outer.values()),
            "maximum_populations_complete_in_one_outer_dataset": max(complete_primary_by_outer.values(), default=0),
        },
        "accounting": {
            "by_status_library": dict(sorted(library_status.items())),
            "useful_cpu_h_recomputed": accounted_useful,
            "useful_cpu_h_saved": summary["useful_cpu_h"],
            "discarded_cpu_h_recomputed": accounted_discarded,
            "discarded_cpu_h_saved": summary["discarded_cpu_h"],
            "incomplete_discarded_cpu_h": incomplete_discarded,
            "incomplete_share_of_accounted_discarded": incomplete_discarded / accounted_discarded,
            "invalid_rows_have_no_cpu_fields": all("useful_cpu_h" not in row and "discarded_cpu_h" not in row for row in rows if row["status"] == "invalid"),
            "reported_totals_exclude_invalid_settings": bool(invalid),
        },
        "journal_guard_experiments": journal_checks(load_runner()),
    }
    assert result["summary_contract"]["status_recomputed"] == {"COMPLETE": 183, "incomplete": 7076, "invalid": 13}
    assert result["summary_contract"]["error_dirs_equal_invalid_dirs"]
    assert result["summary_contract"]["invalid_recheck_terminal_markers"] == {"FAILED": 8, "None": 4, "COMPLETE": 1}
    assert result["fixed_denominators"]["primary_rows_per_population_scenario"] == [200]
    assert result["fixed_denominators"]["check_rows_per_population_scenario"] == [2]
    assert math.isclose(accounted_useful, summary["useful_cpu_h"], rel_tol=0, abs_tol=1e-8)
    assert math.isclose(accounted_discarded, summary["discarded_cpu_h"], rel_tol=0, abs_tol=1e-8)
    assert all(result["journal_guard_experiments"][key] for key in (
        "terminal_uncommitted_duplicate_tail_rejected",
        "nonterminal_duplicate_tail_excluded",
        "committed_duplicate_identity_rejected",
        "coherent_structural_record_not_recomputed",
    ))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
