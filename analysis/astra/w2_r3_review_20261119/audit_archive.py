"""Audit collector 876194 from its archived bytes, bound inputs and previous inventory."""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import platform
import statistics
import sys
import tarfile

import numpy as np


DIGESTS = {
    "archive": "a6959a80cab77ef6fd7667f348cf611f3cb329e9fc4063f990169d648e85fffa",
    "summary": "fc376cd2d741ed4fdf6283607a198f6f8158ceecd8bcd7e8b3906e6ed403acbb",
    "settings": "fa7728290d33fb3f0baf30603d731c769de925739815d9a3b4efb77ddb97b9cd",
    "metric": "2dc57d9f1b27da08b193d2fbd9b94ff24f721f45052483a22d6d35b779a85ff0",
    "runner": "92674ee8aa685b2a20bf5a689a3cbba836b195b8657ba8f79c5da161f315b765",
    "round2_summary": "beabe2d1678fe45b5c74fbd42db6153adaa2cd72ddfc3b25abec1177377f703b",
}
IDENTITY = ("index", "pop", "n", "outer", "library")
COUNTERS = ("executions", "dead_executions", "open_executions")
THETA_LIMITS = {"s": (0, 1), "f": (0.01, 2), "sigma": (0.02, 1), "rho": (0, 0.9),
                "p_c": (0, 0.05), "delta": (0.5, 0.95)}


def indexed(rows):
    result = {r["dir"]: r for r in rows}
    assert len(result) == len(rows)
    return result


def check_calibration(paths, flags, scale, outer):
    # Three coordinates used by the fixed metric. Exclude the final census.
    changes = np.diff(np.log(paths[:, :-1]), axis=1)
    centered = changes - changes.mean(axis=1, keepdims=True)
    ss = np.sum(centered * centered, axis=1)
    lag = np.sum(centered[:, :-1] * centered[:, 1:], axis=1)
    acf = np.divide(lag, ss, out=np.zeros_like(ss), where=ss > 0)
    features = np.column_stack(((changes ** 2).mean(axis=1), acf, (changes > 0).mean(axis=1)))
    keep = np.asarray(scale["keep"])
    diff = features[:, keep] / np.asarray(scale["mad"])[keep] - outer["q"]
    radius = outer["radius"]
    if radius == 0:
        inside = boundary = (diff == 0).all(axis=1)
    else:
        distances = np.sqrt((diff ** 2).sum(axis=1))
        inside, boundary = distances <= radius, distances == radius
    assert inside.all(), f"{int((~inside).sum())} records outside calibration radius"
    assert np.array_equal(boundary, flags), "stored boundary flags differ"


def check_library(raw, row, setting, metric, k, batch_size):
    assert hashlib.sha256(raw).hexdigest() == row["library_sha256"]
    lines = raw.splitlines(keepends=True)
    assert len(lines) == k and raw.endswith(b"\n")
    outer = metric["outers"][f"{setting['pop']}|{setting['outer']}"]
    target = outer["recorded"]
    prev = (-1, -1)
    trajectories, boundaries = [], []
    pilot = setting["pilot"]
    pilot_bytes = hashlib.sha256()
    pilot_count = 0
    for line in lines:
        rec = json.loads(line)
        assert rec.keys() == {"batch", "proposal_in_batch", "boundary", "theta", "recorded"}
        batch, proposal = rec["batch"], rec["proposal_in_batch"]
        assert type(batch) is int and type(proposal) is int
        assert prev < (batch, proposal) and 0 <= batch < row["prefix_end_batch"] and 0 <= proposal < batch_size
        prev = (batch, proposal)
        if pilot and batch < pilot["batches_done"]:
            pilot_bytes.update(line)
            pilot_count += 1
        theta = rec["theta"]
        assert theta.keys() == THETA_LIMITS.keys() and all(
            type(theta[key]) is float and lo <= theta[key] <= hi for key, (lo, hi) in THETA_LIMITS.items()
        )
        assert type(rec["boundary"]) is bool
        y = rec["recorded"]
        assert len(y) == len(target) and all(type(v) is int for v in y)
        assert y[0] == target[0] and all(v > 1 for v in y[:-1]) and y[-1] in (0, 1) and max(y) <= 10**9
        trajectories.append(y)
        boundaries.append(rec["boundary"])
    if pilot:
        # These pilot journals are shorter than K and can be compared in full.
        assert pilot_count == pilot["hits"] < k and pilot_bytes.hexdigest() == pilot["journal_sha256"]
    assert prev[0] == row["kth_hit"]
    check_calibration(np.array(trajectories, dtype=np.float64), boundaries, metric["pops"][setting["pop"]], outer)
    return pilot_count, sum(boundaries)


def summarize(rows, settings, old):
    by_status = {}
    for status in ("COMPLETE", "CAPPED", "incomplete"):
        rs = [r for r in rows.values() if r["status"] == status]
        by_status[status] = {
            "settings": len(rs), "libraries": dict(Counter(r["library"] for r in rs)),
            "settings_with_a_dead_execution": sum(r["dead_executions"] > 0 for r in rs),
            "settings_with_an_open_execution": sum(r["open_executions"] > 0 for r in rs),
            **{key: sum(r[key] for r in rs) for key in COUNTERS},
        }
    incomplete = [r for r in rows.values() if r["status"] == "incomplete"]
    lows = [r for r in incomplete if r["prefix_hits"] < 500]
    zero = [r for r in lows if r["prefix_hits"] == 0]
    retained = {d: r for d, r in old.items() if r["status"] == "COMPLETE"}
    assert not (retained.keys() & rows.keys())
    wave = retained | rows
    primary = defaultdict(list)
    for r in wave.values():
        if r["library"] == "primary":
            primary[r["outer"]].append(r)
    assert len(primary) == 800 and all(len(g) == len({r["pop"] for r in g}) == 9 for g in primary.values())
    coverage = Counter(sum(r["status"] == "COMPLETE" for r in group) for group in primary.values())
    return {
        "by_status": by_status,
        "dead_executions_per_setting_histogram": dict(sorted(Counter(r["dead_executions"] for r in rows.values()).items())),
        "settings_with_any_execution": sum(r["executions"] > 0 for r in rows.values()),
        "incomplete_prefix": {
            "zero_hits": len(zero), "one_to_499": len(lows) - len(zero),
            "500_to_1499": sum(500 <= r["prefix_hits"] < 1500 for r in incomplete),
            "1500_to_1999": sum(1500 <= r["prefix_hits"] < 2000 for r in incomplete),
            "median": statistics.median(r["prefix_hits"] for r in incomplete),
            "zero_hits_no_pilot_no_execution": sum(not settings[r["dir"]]["pilot"] and r["executions"] == 0 for r in zero),
            "zero_hits_with_open_execution": sum(r["open_executions"] > 0 for r in zero),
            "below_500_with_open_execution": sum(r["open_executions"] > 0 for r in lows),
            "below_500_no_execution": sum(r["executions"] == 0 for r in lows),
            "all_incomplete_no_execution": sum(r["executions"] == 0 for r in incomplete),
        },
        "retained_round2_complete": len(retained),
        "combined_completed_primary_populations_per_outer": dict(sorted(coverage.items())),
        "combined_complete_nine_population_primary_outers": sorted(
            outer for outer, group in primary.items() if all(r["status"] == "COMPLETE" for r in group)
        ),
    }


def audit(root):
    base = root / "v2_dev/p3"
    stage = root / "r3d_rehearse_pos"
    files = {
        "archive": base / "w2_r3a/W2.tar.gz", "summary": base / "w2_r3a/collect_W2.json",
        "round2_summary": base / "w2_r2b/collect_W2_b.json", "metric": base / "p3_metric.json",
        "settings": stage / "s1b/p3_settings_r3.json",
        "runner": stage / "src/analysis/fable/calibration/v2_dev/p3_stage1b.py",
    }
    hashes = {}
    for key, path in files.items():
        with path.open("rb") as f:
            hashes[key] = hashlib.file_digest(f, "sha256").hexdigest()
    assert hashes == DIGESTS
    summary_bytes = files["summary"].read_bytes()
    c = json.loads(summary_bytes)
    b = json.loads(files["settings"].read_bytes())
    metric = json.loads(files["metric"].read_bytes())
    rows = indexed(c["rows"])
    old = indexed(json.loads(files["round2_summary"].read_bytes())["rows"])
    settings = indexed([s for s in b["settings"] if s["wave"] == "W2"])
    assert len(b["settings"]) == 6935 and b["K"] == 2000 and b["batch"] == 20000
    assert c["binding"] == {key + "_sha256": hashes[key] for key in ("settings", "metric", "runner")}
    assert all(c["binding"][key] == b[key] for key in ("metric_sha256", "runner_sha256"))
    assert c["wave"] == c["tag"] == "W2" and c["collection_ok"] is True and c["n_errors"] == 0 and c["errors"] == []
    assert len(rows) == 6917 and rows.keys() == settings.keys() == {
        d for d, r in old.items() if r["status"] in ("incomplete", "FAILED", "invalid")
    }
    counts = Counter(r["status"] for r in rows.values())
    assert c["status"] == {key: counts[key] for key in ("COMPLETE", "CAPPED", "FAILED", "incomplete")}
    assert counts == {"COMPLETE": 2728, "CAPPED": 54, "incomplete": 4135}
    assert sorted(c["incomplete"]) == sorted(d for d, r in rows.items() if r["status"] == "incomplete")
    for d, r in rows.items():
        st = settings[d]
        assert all(r[key] == st[key] == old[d][key] for key in IDENTITY)
        assert 0 <= r["prefix_end_batch"] <= st["cap_batches"] and r["prefix_hits"] >= 0
        assert all(type(r[key]) is int and r[key] >= 0 for key in COUNTERS + ("ranges",))
        assert r["dead_executions"] + r["open_executions"] <= r["executions"] and r["open_executions"] <= r["ranges"]
        assert all(math.isfinite(r[key]) and r[key] >= 0 for key in ("useful_cpu_h", "discarded_cpu_h"))
        complete = r["status"] == "COMPLETE"
        assert ("library_sha256" in r) == ("kth_hit" in r) == complete == (r["prefix_hits"] >= b["K"])
        if r["status"] == "CAPPED":
            assert r["prefix_end_batch"] == st["cap_batches"]
    for key in COUNTERS:
        assert sum(r[key] for r in rows.values()) == c[key]
    for key in ("useful_cpu_h", "discarded_cpu_h"):
        assert math.isclose(math.fsum(r[key] for r in rows.values()), c[key], rel_tol=1e-12)

    expected_libs = {f"lib/{d}.jsonl": r for d, r in rows.items() if r["status"] == "COMPLETE"}
    expected_names = set(expected_libs) | {"collect_W2.json", "collect_W2.log"}
    seen = set()
    checked = total_records = boundaries = pilot_libraries = pilot_records = 0
    with tarfile.open(files["archive"], "r|gz") as archive:
        for member in archive:
            name = member.name
            assert member.isfile() and name in expected_names and name not in seen, name
            seen.add(name)
            raw = archive.extractfile(member).read()
            assert len(raw) == member.size
            if name == "collect_W2.json":
                assert raw == summary_bytes
            elif name == "collect_W2.log":
                assert raw.decode().split() == (
                    f"collection_ok True W2 {c['status']} useful {c['useful_cpu_h']:.1f} "
                    f"discarded {c['discarded_cpu_h']:.1f} incomplete {len(c['incomplete'])} errors 0"
                ).split()
            else:
                row = expected_libs[name]
                st = settings[row["dir"]]
                try:
                    n_pilot, n_boundary = check_library(raw, row, st, metric, b["K"], b["batch"])
                except Exception as exc:
                    raise RuntimeError(f"failed audit of {name}: {exc}") from exc
                checked += 1
                total_records += b["K"]
                boundaries += n_boundary
                pilot_libraries += st["pilot"] is not None
                pilot_records += n_pilot
    assert seen == expected_names and total_records == 5456000
    return {
        "collector": "876194", "hashes": hashes, "python": platform.python_version(), "numpy": np.__version__,
        "archive_bytes": files["archive"].stat().st_size, "regular_unique_members": len(seen),
        "embedded_summary_byte_identical": True, "library_hashes_and_counts_verified": checked,
        "records_checked_for_schema_order_extinction_parameter_support_and_calibration": total_records,
        "verified_boundary_flags_true": boundaries, "complete_libraries_with_bound_pilot": pilot_libraries,
        "pilot_prefix_records_verified_byte_for_byte_by_bound_digest": pilot_records,
        "summary": {key: c[key] for key in ("status", "n_errors", *COUNTERS, "queue_left", "claims_left",
                                             "useful_cpu_h", "discarded_cpu_h")},
        **summarize(rows, settings, old),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="parent of v2_dev and r3d_rehearse_pos on deep")
    args = parser.parse_args()
    if not __debug__:
        sys.exit("Run with Python assertions enabled.")
    print(json.dumps(audit(args.root), indent=2, allow_nan=False))
