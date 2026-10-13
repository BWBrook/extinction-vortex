"""Bounded A-screen contract audit; no R fits, population simulations or bank loads.

Run from any directory with NumPy/SciPy, for example:
OPENBLAS_NUM_THREADS=1 /home/bwbrook/papers/dsipa-dev/.venv/bin/python analysis/astra/a_screen_review/contract_checks.py
Only contract_checks.json is retained; all mocked fixtures use a temporary directory.
"""
from contextlib import ExitStack, redirect_stdout
from datetime import datetime
import csv
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch
from zoneinfo import ZoneInfo

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
os.chdir(ROOT)
SOURCE = Path("analysis/fable/calibration/v2_dev/a_screen.py")
ARCHIVE = SOURCE.parent / "a_screen"
MANIFEST = Path("analysis/fable/calibration/freeze_v1/validation_manifest.json")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def dump(path, value):
    Path(path).write_text(json.dumps(value))


def local_checks(m):
    man = json.loads(MANIFEST.read_text())
    od = json.loads((ARCHIVE / "a_outers.json").read_text())
    report = json.loads((ARCHIVE / "a_screen_report.json").read_text())
    rows = [json.loads(line) for s in range(2)
            for line in (ARCHIVE / f"slot{s}/e2e_rows.jsonl").read_text().splitlines()]
    by_id = {r["trial_id"]: r for r in rows}
    metas = [json.loads((ARCHIVE / f"slot{s}/e2e_meta.json").read_text()) for s in range(2)]
    hashes = {Path(line.split()[1]).name: line.split()[0]
              for line in (ARCHIVE / "runner_sha256.txt").read_text().splitlines()}
    source_at_binding = git("show", f"6316a90:{SOURCE}")
    source_now = SOURCE.read_bytes()
    driver = SOURCE.parent / "run_a_screen.sh"
    paired = [0, 0, 0, 0]
    for o in od["outers"]:
        a, v = by_id[o["trial"]]["outcome"] != "accept", o["v1"]["outcome"] != "accept"
        paired[0 if a and v else 1 if v else 2 if a else 3] += 1
    c = {
        "runner_unchanged_since_6316a90": source_at_binding == source_now,
        "driver_unchanged_since_6316a90": git("show", f"6316a90:{driver}") == driver.read_bytes(),
        "archived_runner_hashes_match_bound_source": all(
            hashlib.sha256(git("show", f"6316a90:{SOURCE.parent / name}")).hexdigest() == h
            for name, h in hashes.items()),
        "archived_runner_hashes_match_current_source": all(sha(SOURCE.parent / name) == h for name, h in hashes.items()),
        "metas_current_runner_hash": all(x["runner_sha256"] == sha(SOURCE) for x in metas),
        "manifest_digest_matches": all(x["manifest_digest"] == sha(MANIFEST) == od["manifest_digest"] for x in metas),
        "frozen_source_hashes_match": all(sha(p) == h for p, h in man["source_sha256"].items()),
        "outers_hash_matches": all(x["outers_sha256"] == sha(ARCHIVE / "a_outers.json") for x in metas),
        "first_200_complete_unique": len(rows) == 200 and sorted(by_id) == list(range(200))
            and [o["trial"] for o in od["outers"]] == list(range(200)),
        "declared_chunks_c00_c01": [c["dir"] for c in m.b3_chunks(man)] == list(od["source_rows_sha256"]),
        "outer_chunk_assignment_correct": all(o["dir"] == m.b3_chunks(man)[o["trial"] // 100]["dir"] for o in od["outers"]),
        "all_1800_recorded_series_match": all(by_id[o["trial"]]["selected"][n]["recorded"] == rec
            for o in od["outers"] for n, rec in o["recorded"].items()),
        "slot_assignments_correct": all(all(json.loads(line)["trial_id"] % 2 == s
            for line in (ARCHIVE / f"slot{s}/e2e_rows.jsonl").read_text().splitlines()) for s in range(2)),
        "settings_match_prespecification": all(x["K"] == x["R_train"] == x["R_test"] == 2000
            and x["seed_base"] == 8000006100000 and x["features"] == list(m.CPLUS)
            and x["smoke"] is False and x["nslots"] == 2 for x in metas),
        "reported_paired_table_matches_rows": paired == report["table_both_V1_only_A_only_neither"],
        "no_recorded_failures_or_indeterminates": all(r["outcome"] in ("accept", "reject")
            and r["fit_failures"] == r["train_fail"] == r["test_fail"] == 0 for r in rows),
        "all_observed_reused_without_simulation": all(v["draws"] == 0 and v["params"] == {}
            for r in rows for v in r["selected"].values()),
    }
    return {"checks": c, "paired_table": paired, "population_series_compared": 1800,
            "frozen_source_files": len(man["source_sha256"]),
            "pre_fit_timing": {"commit_6316a90": git("show", "-s", "--format=%cI", "6316a90").decode().strip(),
                               "timeline": (ARCHIVE / "timeline.txt").read_text().splitlines(),
                               "interpretation": "Binding follows wrapper launch, precedes first bank-ready log; consistent with pre-fit binding."},
            "limits": "Source v1 rows, raw T and neighbour payloads are remote; independent parent audit owns those checks."}


def fixture(m, mode):
    """Two synthetic input series, one mocked eight-row bank, synthetic T matrices.

    Actual C+ construction, trees, frozen run_chunk, p_bounds and report execute.
    Only bank loading/design and R fitting are substituted. No scientific outcomes.
    """
    np = m.np
    rec = np.array([[40, 20, 10, 4, 1], [40, 30, 20, 6, 0], [40, 35, 11, 3, 0],
                    [40, 15, 23, 4, 1], [40, 32, 17, 2, 0], [40, 22, 25, 5, 1],
                    [40, 37, 12, 6, 0], [40, 18, 13, 3, 0]])
    fit_calls, loaded, hash_reads, reference_membership = [], [], [], []
    with TemporaryDirectory(prefix="astra_a_contract_") as tmp, ExitStack() as st:
        p = Path(tmp); out = p / "out"; out.mkdir(); baseline = p / "v1"; baseline.mkdir()
        source = p / "source.py"; source.write_text("# fixture source\n")
        rows_path = baseline / "e2e_rows.jsonl"; rows_path.write_text("fixture source rows\n")
        man = {"K": 4, "R": 8, "variant": "ar_cat", "bankdir": "bank",
               "source_sha256": {str(source): sha(source)},
               "bank_sha256": {"mocked_payload.npz": "declared_hash_never_checked"}}
        mp = p / "manifest.json"; dump(mp, man)
        od = {"manifest_digest": sha(mp), "block": "null_low_s",
              "source_rows_sha256": {"v1": sha(rows_path)},
              "outers": [{"trial": i, "dir": "v1", "recorded": {"p": rec[i].tolist()},
                          "v1": {"outcome": "accept", "kth_dist": json.dumps({"p": 0.1})}} for i in range(2)]}
        op = p / "outers.json"; dump(op, od)

        def mock_bank(*args):
            loaded.append([str(a) for a in args])
            return {"rec": rec, "draw_id": np.arange(len(rec))}

        def fits(path_in, path_out, workers):
            fit_calls.append(Path(path_out).name)
            with open(path_in) as f:
                seq = list(csv.DictReader(f))
            tid = int(Path(path_out).stem.split("_")[1])
            features = m.cplus(rec); mad = np.median(np.abs(features - np.median(features, 0)), 0); keep = mad > 0
            tree = m.cKDTree(features[:, keep] / mad[keep])
            _, idx = tree.query(m.cplus(rec[tid:tid + 1])[0][keep] / mad[keep], k=4)
            reference_membership.extend(any([int(r["N"]) for r in seq if int(r["set"]) == s] == rec[j].tolist()
                                            for j in idx) for s in range(1, 17))
            values = np.random.default_rng(1200 + tid).normal(size=(17, 4))
            values = np.column_stack([np.arange(17), values, np.zeros((17, 2))])
            np.savetxt(path_out, values, delimiter=",", header="set,T1,T2,T3,T4,failed,fallback", comments="")
            np.savetxt(baseline / Path(path_out).name, values, delimiter=",",
                       header="set,T1,T2,T3,T4,failed,fallback", comments="")

        original_sha = m.sha
        def logged_sha(path):
            hash_reads.append(str(path)); return original_sha(path)

        for obj, name, val in [(m, "IDS", range(2)), (m, "SMOKE", False),
                              (m, "designs", lambda: {"p": {"years": list(range(5))}}),
                              (m, "load_bank", mock_bank), (m, "sha", logged_sha),
                              (m.e2e, "run_fits", fits), (m.e2e, "calib_features", m.calib_features)]:
            st.enter_context(patch.object(obj, name, val))
        st.enter_context(redirect_stdout(io.StringIO()))
        for slot in range(2):
            m.run(str(mp), tmp, str(op), str(out), slot, 2, 1)
        fit_calls.clear()
        meta_p = out / "slot0/e2e_meta.json"; row_p = out / "slot0/e2e_rows.jsonl"
        nbr_p = out / "slot0/neighbours.npz"
        if mode == "resume_missing_meta":
            meta_p.unlink()
        elif mode == "resume_changed_meta":
            meta = json.loads(meta_p.read_text()); meta["seed_base"] += 1; dump(meta_p, meta)
        elif mode == "resume_duplicate_rows":
            row_p.write_text(row_p.read_text() * 2)
        elif mode == "resume_missing_neighbours":
            nbr_p.unlink()
        elif mode == "resume_missing_T":
            (out / "slot0/T_0.csv").unlink()
        elif mode == "report_missing_neighbour_receipt":
            nbr = dict(np.load(nbr_p)); del nbr["0/p/origC_max"]; np.savez_compressed(nbr_p, **nbr)
        elif mode == "report_wrong_kth":
            nbr = dict(np.load(nbr_p)); nbr["0/p/kth"] += 10; np.savez_compressed(nbr_p, **nbr)
        elif mode == "report_changed_outer_record":
            row = json.loads(row_p.read_text()); row["selected"]["p"]["recorded"][0] += 10
            row_p.write_text(json.dumps(row) + "\n")
        elif mode == "report_changed_source":
            source.write_text("# changed fixture source\n")
        elif mode in ("report_wrong_runner", "report_wrong_settings"):
            for slot in range(2):
                path = out / f"slot{slot}/e2e_meta.json"; meta = json.loads(path.read_text())
                if mode == "report_wrong_runner":
                    meta["runner_sha256"] = "incorrect"
                else:
                    meta.update(K=400, R_train=800, R_test=800, seed_base=0, features=["wrong"])
                dump(path, meta)
        error, result = None, None
        try:
            if mode.startswith("resume"):
                m.run(str(mp), tmp, str(op), str(out), 0, 2, 1)
            else:
                m.report(str(mp), tmp, str(op), str(out), 2, str(p / "report.json"))
                result = json.loads((p / "report.json").read_text())
        except (SystemExit, FileNotFoundError, KeyError, ValueError) as exc:
            error = type(exc).__name__ + ": " + str(exc)
        return {"refused": error is not None, "error": error,
                "additional_mock_fits": len(fit_calls),
                "all_reference_rows_from_Cplus_K_query": all(reference_membership),
                "bank_hashes_checked": any("mocked_payload.npz" in name for name in hash_reads),
                "report_all_checks_true": all(result["checks"].values()) if result else None}


def main():
    spec = importlib.util.spec_from_file_location("a_screen_audit_target", SOURCE)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    import scipy
    modes = ["report_baseline", "resume_complete", "resume_missing_meta", "resume_changed_meta",
             "resume_duplicate_rows", "resume_missing_neighbours", "resume_missing_T",
             "report_missing_neighbour_receipt", "report_wrong_kth", "report_changed_source",
             "report_wrong_runner", "report_wrong_settings", "report_changed_outer_record"]
    fixtures = {mode: fixture(m, mode) for mode in modes}
    local = local_checks(m)
    assert all(local["checks"].values()), local["checks"]
    expected_refusals = {"resume_missing_meta", "resume_changed_meta", "resume_duplicate_rows",
                         "resume_missing_neighbours", "report_missing_neighbour_receipt",
                         "report_wrong_kth", "report_changed_source"}
    assert all(r["refused"] == (mode in expected_refusals) for mode, r in fixtures.items()), fixtures
    assert all(r["all_reference_rows_from_Cplus_K_query"] for r in fixtures.values())
    result = {"scope": "Independent contract audit; tiny synthetic/mocked fixtures, no R fits or production bank loads",
              "time_hobart": datetime.now(ZoneInfo("Australia/Hobart")).isoformat(),
              "head": git("rev-parse", "HEAD").decode().strip(),
              "runtime": {"python": platform.python_version(), "numpy": m.np.__version__, "scipy": scipy.__version__},
              "observed_receipts": local, "mocked_contract_cases": fixtures,
              "interpretation": {
                  "completed_run": "Compact records match declared cases, source, settings, pairing, and zero failures; remote raw-T audit is separate.",
                  "latent_binding_gap": "No bank hash validation; report accepts consistently wrong runner/settings and changed row-level observed series. Not observed in completed run.",
                  "latent_resume_gap": "Missing raw T does not prevent resume skip, although report would encounter missing T. Existing missing-meta/changed-meta/duplicate/neighbour guards work.",
                  "power_screen": "Paired first-300 b5/b16 comparisons can quantify detection trade-offs, not causally identify diffuse reference as the mechanism."}}
    target = Path(__file__).with_suffix(".json"); target.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(target), "observed_checks": len(local["checks"]),
                      "mock_cases": len(fixtures), "expected_refusals": len(expected_refusals)}))


if __name__ == "__main__":
    main()
