"""Bounded synthetic audit of the repaired Stage 1b comparator.

Only temporary JSON journals are generated; there is no sampling, fitting,
production archive access or change to the implementation under review.
"""
import contextlib
from datetime import datetime
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import time
import tracemalloc
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
V2 = ROOT / "analysis/fable/calibration/v2_dev"
SOURCE = V2 / "p3_r2_determinism.py"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def line(batch, proposal=7, value=.5):
    return (json.dumps(dict(batch=batch, proposal_in_batch=proposal,
                           theta={"s": value}), sort_keys=True) + "\n").encode()


def shard(run, setting="s00001", first=0, count=1, lines=(),
          filename=None, checkpoint_patch=None, data_suffix=b""):
    folder = run / "sets" / setting
    folder.mkdir(parents=True, exist_ok=True)
    stem = filename or f"sh{first:09d}"
    data = b"".join(lines)
    state = dict(first_batch=first, batches_done=count,
                 journal_bytes=len(data), journal_sha256=digest(data),
                 hits=len(lines))
    state.update(checkpoint_patch or {})
    (folder / (stem + ".json")).write_text(json.dumps(state))
    (folder / (stem + "_hits.jsonl")).write_bytes(data + data_suffix)


def main():
    spec = importlib.util.spec_from_file_location("reviewed_comparator", SOURCE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    cases = []

    def case(name, build, expected_exit, expected=None, finding=None,
             requested=("s00001",), trace=False):
        with tempfile.TemporaryDirectory(prefix="s1b-closure-") as tmp:
            base = Path(tmp)
            a, b = base / "a", base / "b"
            build(a, b)
            dirs, out = base / "dirs.txt", base / "out.json"
            dirs.write_text("\n".join(requested) + "\n")
            if trace:
                tracemalloc.start()
            started = time.perf_counter()
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    mod.main(str(a), str(b), str(dirs), str(out))
            except SystemExit as ex:
                code = ex.code
            else:
                raise AssertionError("Comparator did not set an exit code")
            elapsed = time.perf_counter() - started
            peak = tracemalloc.get_traced_memory()[1] if trace else None
            if trace:
                tracemalloc.stop()
            result = json.loads(out.read_text())
            assert code == result["exit"] == expected_exit, (name, code, result)
            for key, value in (expected or {}).items():
                assert result["total"][key] == value, (name, key, result)
            if trace:
                assert peak < 2_000_000, peak
            cases.append(dict(name=name, exit=code, total=result["total"],
                              problems=result["problems"], settings=result["settings"],
                              seconds=elapsed, traced_peak_bytes=peak,
                              remaining_issue=finding))

    def pair(a, b, **kwargs):
        for run in (a, b):
            shard(run, **kwargs)

    case("identical_records", lambda a,b: pair(a,b,count=2,lines=[line(0),line(1)]),
         0, dict(batches_compared=2, records_compared=2, identical=2))

    def sparse_gaps(a, b):
        shard(a, first=0, count=4, lines=[line(0),line(2),line(3)])
        shard(a, first=8, count=4, lines=[line(8),line(10),line(11)])
        shard(b, first=2, count=4, lines=[line(2),line(3),line(4)])
        shard(b, first=10, count=4, lines=[line(10),line(11),line(12)])
    case("sparse_gaps_and_half_open_boundaries", sparse_gaps, 0,
         dict(batches_compared=4, records_compared=4, identical=4))
    case("positive_batch_overlap_without_hits", lambda a,b: pair(a,b,count=5), 0,
         dict(batches_compared=5, records_compared=0))
    case("huge_batch_interval_tiny_journal",
         lambda a,b: pair(a,b,count=381_823_099,lines=[line(381_823_098)]), 0,
         dict(batches_compared=381_823_099, records_compared=1, identical=1), trace=True)

    def no_overlap(a, b):
        shard(a, count=2, lines=[line(0)])
        shard(b, first=2, count=2, lines=[line(2)])
    case("no_overlap", no_overlap, 1, dict(batches_compared=0, records_compared=0))

    def missing(a, b):
        pair(a,b,lines=[line(0)])
    case("missing_requested_directory", missing, 1,
         requested=("s00001","s99999"))

    def invalid(a, b, patch=None, lines=None):
        shard(a, lines=lines if lines is not None else [line(0)], checkpoint_patch=patch)
        shard(b, lines=[line(0)])
    case("wrong_hash", lambda a,b: invalid(a,b,{"journal_sha256":"wrong"}), 1)
    case("short_committed_journal",
         lambda a,b: invalid(a,b,{"journal_bytes":len(line(0))+1}), 1)
    case("record_outside_committed_batches", lambda a,b: invalid(a,b,lines=[line(1)]), 1)
    case("malformed_json_record", lambda a,b: invalid(a,b,lines=[b"{broken}\n"]), 1)
    case("missing_record_identity", lambda a,b: invalid(a,b,lines=[b'{"batch":0}\n']), 1)

    def unmatched(a, b):
        shard(a, lines=[line(0,7)])
        shard(b, lines=[line(0,8)])
    case("identity_difference", unmatched, 1, dict(records_compared=2, unmatched=2))
    def bytes_changed(a, b):
        shard(a, lines=[line(0,value=.5)])
        shard(b, lines=[line(0,value=.5000000000000001)])
    case("byte_only_difference", bytes_changed, 2,
         dict(records_compared=1, bytes_differ=1, unmatched=0))

    def prefix(a, b):
        shard(a, lines=[line(0)], data_suffix=b"uncommitted garbage")
        shard(b, lines=[line(0)])
    case("uncommitted_suffix_excluded", prefix, 0,
         dict(records_compared=1, identical=1))

    def duplicate(a, b, changed=False):
        shard(a, lines=[line(0,value=.4 if changed else .5), line(0)])
        shard(b, lines=[line(0)])
    case("duplicate_identity_with_valid_hash", duplicate, 0,
         dict(records_compared=1, identical=1),
         finding="Two committed records collapse to one identity; valid hashes do not establish uniqueness.")
    case("conflicting_duplicate_shadowed", lambda a,b: duplicate(a,b,True), 0,
         dict(records_compared=1, identical=1),
         finding="A different earlier record is overwritten by the last duplicate and the comparator exits 0.")

    def overlapping(a, b):
        shard(a, lines=[line(0,value=.4)])
        shard(a, first=0, lines=[line(0)], filename="sh000000001")
        shard(b, lines=[line(0)])
    case("duplicate_identity_across_overlapping_shards", overlapping, 0,
         dict(batches_compared=1, records_compared=1, identical=1),
         finding="Cross-shard identity collisions are overwritten; overlapping checkpoints are not rejected.")
    case("duplicate_requested_setting", lambda a,b: pair(a,b,lines=[line(0)]), 0,
         dict(settings=2, batches_compared=2, records_compared=2, identical=2),
         requested=("s00001","s00001"),
         finding="Duplicate directory lines double aggregate counts while the per-setting result has one entry.")

    def empty_with_positive(a, b):
        pair(a,b,lines=[line(0)])
        for run in (a,b):
            (run/"sets"/"s00002").mkdir()
    case("zero_coverage_setting_explicit_beside_positive", empty_with_positive, 0,
         dict(settings=2,batches_compared=1), requested=("s00001","s00002"))
    # This is expected: the current contract requires aggregate positive
    # coverage, and shared-pilot-only settings legitimately have no new batches.

    def source_binding_scope(a, b):
        pair(a,b,lines=[line(0)])
        (a/"settings.json").write_text('{"stream_tag":"one"}')
        (b/"settings.json").write_text('{"stream_tag":"different"}')
    case("source_binding_is_external_to_comparator", source_binding_scope, 0,
         dict(records_compared=1,identical=1))

    old = json.loads((ROOT/"analysis/astra/s1b_r2_science_review/cost_coverage_checks.json").read_text())
    cost_paths = ["analysis/fable/calibration/v2_dev/p3_w1_costs.py",
                  "analysis/fable/calibration/v2_dev/p3/w1_r1_costs.json",
                  "analysis/fable/calibration/v2_dev/p3/w1_r1_collect_W1.json",
                  "analysis/fable/calibration/v2_dev/p2/s1a_main/collect_deep.json"]
    unchanged = {}
    for path in cost_paths:
        earlier = subprocess.check_output(["git","show",f"b34b5e1:{path}"],cwd=ROOT)
        current = (ROOT/path).read_bytes()
        assert earlier == current, path
        unchanged[path] = digest(current)
    receipt = dict(timestamp=datetime.now(ZoneInfo("Australia/Hobart")).isoformat(),
                   target_head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
                   comparator_sha256=digest(SOURCE.read_bytes()), cases=cases,
                   case_count=len(cases), unchanged_cost_sources_and_inputs=unchanged,
                   earlier_independent_cost_input_hashes=old["inputs_sha256"],
                   design_sha256=digest((ROOT/"notes/vortex_stage1b_design_20261016.md").read_bytes()),
                   note_sha256=digest((V2/"NOTE.md").read_bytes()),
                   interpretation="Sparse coverage and explicit exit codes work. Duplicate identities remain unvalidated; aggregate positive coverage and sampling source binding require appropriate external interpretation. No launch blocker from this scope.")
    (HERE/"closure_checks.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps(dict(cases=len(cases),remaining_issue_cases=[c["name"] for c in cases if c["remaining_issue"]],
                         sparse_case=next(c for c in cases if c["name"]=="huge_batch_interval_tiny_journal")),indent=2))


if __name__ == "__main__":
    main()
