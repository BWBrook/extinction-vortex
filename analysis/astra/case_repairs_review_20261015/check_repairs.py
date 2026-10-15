#!/usr/bin/env python3
"""Bounded review of case repairs, using cached sources and a temporary build.

Usage: python3 check_repairs.py SOURCE_DIR OUTPUT.json
Does not write to Fable's artifact directories or amend source snapshots.
"""
import collections
import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT / "analysis/fable/caribou"
FIELDS = ("SURVEY_SUMMARY_DETAIL_ID", "SUMMARY_YEAR", "SUMMARY_MONTH", "SUMMARY_DAY",
          "PARAMETER_METHOD_CODE", "PARAMETER_METHOD_NAME", "PARAMETER_VALUE",
          "BEST_PARAMETER_VALUE", "SUMMARY_DETAIL_NOTE", "SUMMARY_GENERAL_NOTE")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def run(cmd, **kw):
    p = subprocess.run(cmd, check=True, text=True, capture_output=True, **kw)
    return {"command": cmd, "stdout": p.stdout, "stderr": p.stderr}


def lexical(s):
    return collections.Counter(re.findall(r"\w+", unicodedata.normalize("NFKC", s).lower()))


def audit(src):
    tmp = Path(tempfile.mkdtemp(prefix="astra_case_repairs_check_"))
    manifest = json.loads((ART / "caribou_sources.json").read_text())
    hashes = {name: sha(src / name) for name in manifest["files"]}
    assert all(h == manifest["files"][name]["sha256_fable"] for name, h in hashes.items() if name != "wsi_central.json")
    full_wsi = json.loads((src / "wsi_central.json").read_text())
    props = [f["properties"] for f in full_wsi["features"]]
    ind = sorted(({k: r.get(k) for k in FIELDS} for r in props if r.get("PARAMETER_NAME") == "Individuals"),
                 key=lambda r: r["SURVEY_SUMMARY_DETAIL_ID"])
    h = hashlib.sha256(json.dumps(ind, sort_keys=True).encode()).hexdigest()
    old = json.loads((ROOT / "analysis/astra/a_power_review/caribou_source_checks.json").read_text())
    assert ind == sorted(old["wsi"]["individuals_rows"], key=lambda r: r["SURVEY_SUMMARY_DETAIL_ID"])
    assert len(ind) == 23 and h == manifest["wsi_individuals_content_sha256"]
    dem = read(ART / "demographic_evidence.csv")
    source = read(src / "recruitment_counts.csv")
    demographic = []
    for r in dem:
        if r["quantity"].startswith("calves"):
            s = next(x for x in source if x["herd"] == r["herd"] and x["year"] == r["archive_year"])
            expected_year = int(s["year"]) - (s["season"] in ("spring", "fall"))
            assert int(r["survey_calendar_year"]) == expected_year
            assert r["value"] == s["calves"] + "/" + s["adults"]
            demographic.append({"herd": r["herd"], "archive_year": int(r["archive_year"]),
                                "survey_calendar_year": expected_year, "value": r["value"]})
        else:
            assert r["survey_calendar_year"] == ""
    assert collections.Counter(r["herd"] for r in demographic) == {"Maligne": 14, "Purcells Central": 5}
    purcells = read(ART / "purcells_central_census.csv")
    for r in purcells:
        ps = [p for p in ind if p["SUMMARY_YEAR"] == int(r["year"])]
        for col, field in (("wsi_month", "SUMMARY_MONTH"), ("wsi_day", "SUMMARY_DAY")):
            assert r[col] == ";".join(sorted({str(p[field]) for p in ps if p[field] is not None}))
        for col, field in (("wsi_detail_notes", "SUMMARY_DETAIL_NOTE"), ("wsi_general_notes", "SUMMARY_GENERAL_NOTE")):
            assert r[col] == " | ".join(sorted({(p[field] or "").strip() for p in ps} - {""}))
    assert [r["year"] for r in purcells if not r["wsi_day"]] == ["2003", "2005"]

    dest = tmp / "analysis/fable/caribou"
    dest.mkdir(parents=True)
    for name in ("make_caribou.py", "caribou_sources.json"):
        shutil.copy2(ART / name, dest / name)
    wp = tmp / "data/raw/williams2021/population_data.csv"
    wp.parent.mkdir(parents=True)
    shutil.copy2(ROOT / "data/raw/williams2021/population_data.csv", wp)
    rebuild = run(["uv", "run", "--offline", "--with", "matplotlib", "python", str(dest / "make_caribou.py"), str(src)], cwd=tmp)
    generated = ["banff_census.csv", "maligne_census.csv", "purcells_central_census.csv", "demographic_evidence.csv", "caribou_case.png"]
    equal = {name: sha(dest / name) == sha(ART / name) for name in generated}
    assert all(equal.values())

    # Exercise the new hash guard using compact copies of precisely its declared
    # Individuals input. Other static inputs remain read-only symlinks.
    probesrc = tmp / "hash_probe_sources"
    probesrc.mkdir()
    for name in manifest["files"]:
        if name != "wsi_central.json":
            (probesrc / name).symlink_to(src / name)
    probe = tmp / "hash_probe.py"
    probe.write_text('''import copy, importlib.util, json, pathlib, sys
code, source, rows = sys.argv[1:]
sys.argv = [code, source]
spec = importlib.util.spec_from_file_location("case_rebuild", code)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
base = json.loads(pathlib.Path(rows).read_text())
features = [{"id": "arbitrary-"+str(i), "properties": {**p, "PARAMETER_NAME": "Individuals"}} for i,p in enumerate(base)]
cases = {"wrapper_only": {"timeStamp":"arbitrary", "features":features}}
for name, field in (("changed_value", "PARAMETER_VALUE"), ("changed_general_note", "SUMMARY_GENERAL_NOTE")):
    x = copy.deepcopy(cases["wrapper_only"])
    x["features"][0]["properties"][field] = "changed"
    cases[name] = x
x = copy.deepcopy(cases["wrapper_only"]); x["features"].pop(); cases["missing_row"] = x
result = {}
for name, payload in cases.items():
    pathlib.Path(source,"wsi_central.json").write_text(json.dumps(payload))
    try: m.check_hashes(); result[name] = "accepted"
    except SystemExit as e: result[name] = str(e)
assert result["wrapper_only"] == "accepted"
assert all(result[k].startswith("WSI Individuals content ") for k in cases if k != "wrapper_only")
print(json.dumps(result))
''')
    (tmp / "wsi_rows.json").write_text(json.dumps(ind))
    guards = run(["uv", "run", "--offline", "--with", "matplotlib", "python", str(probe),
                  str(dest / "make_caribou.py"), str(probesrc), str(tmp / "wsi_rows.json")], cwd=tmp)

    pdfs = {}
    for name, path in (("nine_series", ROOT / "analysis/fable/tables/nine_series_table.pdf"),
                       ("caribou", ART / "caribou_case.pdf"), ("rebuilt_caribou", dest / "caribou_case.pdf")):
        info = run(["pdfinfo", str(path)])["stdout"]
        check = run(["qpdf", "--check", str(path)])
        run(["pdftoppm", "-png", "-singlefile", "-r", "160", str(path), str(tmp / name)])
        run(["pdftotext", "-layout", str(path), str(tmp / (name + ".txt"))])
        pdfs[name] = {"sha256": sha(path), "pages": int(re.search(r"^Pages:\s+(\d+)", info, re.M)[1]),
                      "info": info, "qpdf": check, "render": str(tmp / (name + ".png")),
                      "text": str(tmp / (name + ".txt"))}
    assert pdfs["nine_series"]["pages"] == 1
    assert sha(tmp / "caribou.png") == sha(tmp / "rebuilt_caribou.png")
    md = (ROOT / "notes/nine_series_evidence_table_20261014.md").read_text()
    body = md.split("---", 2)[2]
    text = (tmp / "nine_series.txt").read_text()
    assert lexical(body) == lexical(text)
    ids = re.findall(r"\(W(\d+)\)", text)
    assert ids == ["14", "15", "6", "20", "21", "10", "4", "8", "9"]
    prior_table = subprocess.check_output(["git", "show", "f2f9ad3:notes/nine_series_evidence_table_20261014.md"], cwd=ROOT, text=True)
    ledger = (ROOT / "notes/nine_series_evidence_ledger_20261014.md").read_text()
    assert "## Notes\n" in prior_table and "## Notes\n" in ledger
    assert prior_table.split("## Notes\n", 1)[1] == ledger.split("## Notes\n", 1)[1]
    unchanged = {}
    for name in ("maligne_census.csv", "banff_census.csv"):
        previous = subprocess.check_output(["git", "show", "f2f9ad3:analysis/fable/caribou/" + name], cwd=ROOT)
        unchanged[name] = previous == (ART / name).read_bytes()
    assert all(unchanged.values())
    return {
        "audit_time": datetime.now(ZoneInfo("Australia/Hobart")).isoformat(),
        "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "baseline": "f2f9ad3", "source_cache": str(src), "source_sha256": hashes,
        "WSI_rows": len(props), "WSI_Individuals": len(ind), "WSI_content_sha256": h,
        "WSI_declared_fields": list(FIELDS), "WSI_matches_prior_receipt": True,
        "hash_guard_probes": json.loads(guards["stdout"]), "demographic_year_crosswalk": demographic,
        "general_notes_years": [r["year"] for r in purcells if r["wsi_general_notes"]],
        "missing_day_years": [r["year"] for r in purcells if not r["wsi_day"]],
        "unchanged_count_tables": unchanged, "temporary_directory": str(tmp), "rebuild": rebuild,
        "rebuilt_bytes_equal": equal, "caribou_PDF_render_equal": True, "PDFs": pdfs,
        "nine_series": {"ids_in_PDF": ids, "source_total_whitespace_words": len(md.split()),
                        "source_body_whitespace_words": len(body.split()),
                        "table_prose_whitespace_words": sum(len(x.strip("|").replace("|", " ").split()) for x in body.splitlines() if x.startswith("|") and not x.startswith("|:")),
                        "source_body_lexical_tokens": sum(lexical(body).values()),
                        "PDF_lexical_tokens": sum(lexical(text).values()), "PDF_source_token_multisets_identical": True,
                        "prior_main_file_whitespace_words": len(prior_table.split()),
                        "ledger_whitespace_words": len(ledger.split()), "ledger_source_notes_unchanged": True},
        "scope": "Repairs only; existing sources and earlier audit evidence. No new source search, model, interval or empirical inference."
    }


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    result = audit(Path(sys.argv[1]).resolve())
    Path(sys.argv[2]).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"receipt": sys.argv[2], "temporary_directory": result["temporary_directory"],
                      "WSI_Individuals": result["WSI_Individuals"], "nine_series": result["nine_series"]}, indent=2))
