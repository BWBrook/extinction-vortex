#!/usr/bin/env python3
"""Audit the delivered caribou artifacts against pinned local snapshots.

Usage: python3 check_caribou.py FABLE_SOURCE_DIR ASTRA_SOURCE_DIR RECEIPT.json
Creates an isolated temporary rebuild; no source or delivered artifact is edited.
"""
import collections
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT / "analysis/fable/caribou"
HERDS = ("Maligne", "Purcells Central", "Banff")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path, encoding="utf-8-sig"):
    with path.open(encoding=encoding, newline="") as f:
        return list(csv.DictReader(f))


def run(args, **kwargs):
    p = subprocess.run(args, text=True, capture_output=True, check=True, **kwargs)
    return {"command": args, "stdout": p.stdout, "stderr": p.stderr}


def audit(src, previous):
    manifest = json.loads((ART / "caribou_sources.json").read_text())
    checks = {}
    for name, expected in manifest["files"].items():
        p = src / name
        checks[name] = {"bytes": p.stat().st_size, "sha256": digest(p)}
        assert checks[name] == {"bytes": expected["bytes"], "sha256": expected["sha256_fable"]}, name

    old = json.loads((previous / "wsi_central.json").read_text())
    new = json.loads((src / "wsi_central.json").read_text())
    assert digest(previous / "wsi_central.json") == manifest["files"]["wsi_central.json"]["sha256_astra"]
    op = [f["properties"] for f in old["features"]]
    np = [f["properties"] for f in new["features"]]
    assert op == np
    assert [f["geometry"] for f in old["features"]] == [f["geometry"] for f in new["features"]]
    ind = [r for r in np if r["PARAMETER_CODE"] == "Individuals"]
    assert ind == [r for r in np if r["PARAMETER_NAME"] == "Individuals"]
    old_receipt = json.loads((ROOT / "analysis/astra/a_power_review/caribou_source_checks.json").read_text())
    assert len(ind) == len(old_receipt["wsi"]["individuals_rows"]) == 23
    wsi = {
        "rows_each": len(np), "individuals_each": len(ind),
        "full_properties_identical": op == np, "geometry_identical": True,
        "top_level_changes": [k for k in old if k != "features" and old[k] != new.get(k)],
        "feature_changed_keys": sorted({k for a, b in zip(old["features"], new["features"]) for k in a if a[k] != b.get(k)}),
        "previous_review_prose_25_is_error": True,
        "general_notes_omitted_from_new_census_table": [
            {k: r[k] for k in ("SURVEY_SUMMARY_DETAIL_ID", "SUMMARY_YEAR", "SUMMARY_MONTH", "SUMMARY_DAY", "SUMMARY_GENERAL_NOTE")}
            for r in ind if r["SUMMARY_GENERAL_NOTE"]],
    }
    counts = rows(src / "counts.csv")
    cr = {(r["herd"], int(r["year"])): r for r in counts if r["herd"] in HERDS}
    williams = {r["ID"]: {int(k): int(float(v)) for k, v in r.items() if k.isdigit() and v not in ("", "NULL")}
                for r in rows(ROOT / "data/raw/williams2021/population_data.csv") if r["ID"] in ("27", "28")}

    # Independent group-by-flight arithmetic, retaining the blank record and all IDs.
    pc = rows(src / "pc.csv", "cp1252")
    assert pc.pop(0)["Unique ID"] == "ID unique"
    ml = [r for r in pc if r["Region"] == "Maligne"]
    flight = collections.defaultdict(list)
    for r in ml:
        if r["Survey type"] == "rut":
            flight[(int(r["Year"]), int(r["Month"]), int(r["Day"]))].append(r)
    flights = []
    for (year, month, day), group in sorted(flight.items()):
        flights.append({
            "survey_year": year, "flight_date": f"{year:04d}-{month:02d}-{day:02d}",
            "group_records": len(group), "ids": [r["Unique ID"] for r in group],
            "blank_total_ids": [r["Unique ID"] for r in group if not r["Total number of individuals"]],
            "recorded_total": sum(int(r["Total number of individuals"]) for r in group if r["Total number of individuals"]),
            "calves": sum(int(v) for r in group for k, v in r.items() if k.startswith("Calf -") and v),
        })
    mt = {int(r["year"]): r for r in rows(ART / "maligne_census.csv")}
    assert len(flights) == 21
    for f in flights:
        r = mt[f["survey_year"]]
        assert r["parks_fall_flight_dates"] == f["flight_date"]
        assert int(r["parks_fall_group_records"]) == f["group_records"]
        assert int(r["parks_fall_sum_recorded_totals"]) == f["recorded_total"]
        assert r["parks_blank_total_ids"] == ";".join(f["blank_total_ids"])
    for y, r in mt.items():
        assert r["lamb_archive_count"] == cr.get(("Maligne", y), {}).get("count", "")
        assert r["williams_id27"] == str(williams["27"].get(y, ""))
    conflicts = [{"year": f["survey_year"], "parks": f["recorded_total"], "archive": int(mt[f["survey_year"]]["lamb_archive_count"])}
                 for f in flights if mt[f["survey_year"]]["lamb_archive_count"] and
                 f["recorded_total"] != int(mt[f["survey_year"]]["lamb_archive_count"])]
    assert [r["year"] for r in conflicts] == [2001, 2003, 2004, 2006, 2008, 2014]

    pt = rows(ART / "purcells_central_census.csv")
    class_checks = []
    for r in pt:
        y = int(r["year"])
        source = [x for x in ind if x["SUMMARY_YEAR"] == y]
        for cls in ("OTC", "MNKA", "MC"):
            vals = [str(x["PARAMETER_VALUE"]) for x in source if x["PARAMETER_METHOD_CODE"] == cls]
            assert r["wsi_" + cls] == ";".join(vals)
        assert set(map(int, r["wsi_detail_ids"].split(";"))) == {x["SURVEY_SUMMARY_DETAIL_ID"] for x in source}
        assert set(r["wsi_best_flagged"].split(";")) == {x["PARAMETER_METHOD_CODE"] for x in source if x["BEST_PARAMETER_VALUE"] == "Yes"}
        ac = cr[("Purcells Central", y)]
        cls = "MNKA" if ac["MinUsed"] == "1" else "OTC"
        assert r["lamb_archive_count"] == ac["count"] == r["wsi_" + cls]
        class_checks.append({"year": y, "archive_count": int(ac["count"]), "MinUsed": ac["MinUsed"], "matching_WSI_class": cls})
    banff = rows(ART / "banff_census.csv")
    for r in banff:
        y = int(r["year"])
        assert int(r["williams_id28"]) == williams["28"][y] == int(cr[("Banff", y)]["count"]) == int(r["lamb_archive_count"])
    assert len(banff) == 16

    dem = rows(ART / "demographic_evidence.csv")
    sr = [r for r in rows(src / "survival.csv") if r["herd"] in HERDS]
    rr = [r for r in rows(src / "recruitment_counts.csv") if r["herd"] in HERDS]
    assert len(dem) == len(sr) + len(rr) == 28
    for r in sr:
        d = next(x for x in dem if x["herd"] == r["herd"] and x["year"] == r["year"] and x["quantity"].startswith("adult female"))
        assert d["value"] == r["est"] and d["uncertainty_as_given"] == f"sd {float(r['sd']):.3f}"
    composition = []
    for r in rr:
        d = next(x for x in dem if x["herd"] == r["herd"] and x["year"] == r["year"] and x["quantity"].startswith("calves"))
        assert d["value"] == r["calves"] + "/" + r["adults"]
        sy = int(r["year"]) - (r["season"] in ("fall", "spring"))
        c = {**r, "survey_calendar_year": sy}
        if r["herd"] == "Maligne":
            f = next(f for f in flights if f["survey_year"] == sy)
            c.update({"PC_flight_date": f["flight_date"], "PC_calves": f["calves"],
                      "PC_recorded_noncalves": f["recorded_total"] - f["calves"],
                      "composition_matches_PC": (int(r["calves"]), int(r["adults"])) == (f["calves"], f["recorded_total"] - f["calves"])})
        composition.append(c)
    treatment = [r for r in rows(src / "treatments.csv") if r["herd"] in HERDS]
    treatment_checks = {}
    for h in HERDS:
        tr = [r for r in treatment if r["herd"] == h]
        treatment_checks[h] = {"years": [min(int(r["year"]) for r in tr), max(int(r["year"]) for r in tr)],
                               "rows": len(tr), "applied_values": sorted({r["applied"] for r in tr}),
                               "zero_years": sorted({int(r["year"]) for r in tr if r["applied"] == "0"}),
                               "NA_years": sorted({int(r["year"]) for r in tr if r["applied"] == "NA"}),
                               "categories": sorted({r["treatment"] for r in tr})}
        assert {r["applied"] for r in tr} <= {"0", "NA"}
    transplants = [r for r in rows(src / "transplants.csv") if "Purcell" in r["herd"]]

    tmp = Path(tempfile.mkdtemp(prefix="astra_caribou_rebuild_"))
    out = tmp / "analysis/fable/caribou"
    out.mkdir(parents=True)
    for name in ("make_caribou.py", "caribou_sources.json"):
        shutil.copy2(ART / name, out / name)
    target = tmp / "data/raw/williams2021/population_data.csv"
    target.parent.mkdir(parents=True)
    shutil.copy2(ROOT / "data/raw/williams2021/population_data.csv", target)
    rebuild = run(["uv", "run", "--offline", "--with", "matplotlib", "python", str(out / "make_caribou.py"), str(src)], cwd=tmp)
    generated = sorted(p.name for p in out.iterdir() if p.name not in ("make_caribou.py", "caribou_sources.json"))
    comparisons = {n: {"byte_equal": digest(out / n) == digest(ART / n), "rebuilt_sha256": digest(out / n), "delivered_sha256": digest(ART / n)}
                   for n in generated}
    assert all(comparisons[n]["byte_equal"] for n in generated if n.endswith(".csv"))
    pdf_check = run(["qpdf", "--check", str(out / "caribou_case.pdf")])
    delivered_pdf_check = run(["qpdf", "--check", str(ART / "caribou_case.pdf")])
    run(["pdftoppm", "-png", "-r", "140", "-singlefile", str(out / "caribou_case.pdf"), str(tmp / "rebuilt_pdf")])
    run(["pdftoppm", "-png", "-r", "140", "-singlefile", str(ART / "caribou_case.pdf"), str(tmp / "delivered_pdf")])
    png_comparison = run(["uv", "run", "--offline", "--with", "matplotlib", "python", "-c",
                          "import json,sys,matplotlib,numpy as np;from PIL import Image; "
                          "a=np.asarray(Image.open(sys.argv[1]));b=np.asarray(Image.open(sys.argv[2])); "
                          "print(json.dumps({'matplotlib':matplotlib.__version__,'shapes_equal':a.shape==b.shape,'pixels_equal':bool(np.array_equal(a,b))}))",
                          str(out / "caribou_case.png"), str(ART / "caribou_case.png")], cwd=tmp)
    return {
        "audited_at": datetime.now(ZoneInfo("Australia/Hobart")).isoformat(),
        "checkout": run(["git", "rev-parse", "HEAD"], cwd=ROOT)["stdout"].strip(),
        "scope": "Pinned-source descriptive audit; no fits, intervals, source amendment or publication",
        "source_hashes": checks, "Williams_input_sha256": digest(ROOT / "data/raw/williams2021/population_data.csv"),
        "WSI_comparison": wsi, "Maligne_flights": flights, "Maligne_count_conflicts": conflicts,
        "Maligne_records_378_423_424": [r for r in ml if r["Unique ID"] in ("378", "423", "424")],
        "Purcells_archive_class_crosswalk": class_checks, "Banff_exact_matches": len(banff),
        "survival_rows": sr, "composition_source_crosswalk": composition,
        "treatment_checks": treatment_checks, "Purcell_transplant_rows": transplants,
        "rebuild": {"temporary_directory": str(tmp), "run": rebuild, "generated_files": generated,
                    "file_comparisons": comparisons, "png_comparison": json.loads(png_comparison["stdout"]),
                    "pdf_check": pdf_check, "delivered_pdf_check": delivered_pdf_check,
                    "pdf_render": str(tmp / "rebuilt_pdf.png"),
                    "PDF_rendered_PNGs_byte_equal": digest(tmp / "rebuilt_pdf.png") == digest(tmp / "delivered_pdf.png"),
                    "events_timeline_generated": (out / "events_timeline.csv").exists()},
        "provenance_limit": "Earlier primary-paper and management-page readings reused; no renewed source search or raw individual-history recovery. Source snapshots remain outside repository."
    }


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    receipt = audit(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())
    Path(sys.argv[3]).write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": sys.argv[3], "temporary_directory": receipt["rebuild"]["temporary_directory"],
                      "WSI_individuals": receipt["WSI_comparison"]["individuals_each"],
                      "Maligne_flights": len(receipt["Maligne_flights"]), "Banff_matches": receipt["Banff_exact_matches"],
                      "png_comparison": receipt["rebuild"]["png_comparison"]}, indent=2))
