#!/usr/bin/env python3
"""Re-tabulate public caribou source snapshots; no fitting or imputation.

Usage: python3 caribou_source_checks.py /tmp/astra_caribou_20261014 OUTPUT.json
Required input filenames and retrieval URLs are recorded in the output manifest.
The WSI snapshot may contain GeoJSON or a list of feature properties; geometry
is ignored. Missing group totals remain flagged, never inferred as zero.
"""
import collections
import csv
import hashlib
import json
import pathlib
import sys
import urllib.parse


def audit(root):
    git = "https://raw.githubusercontent.com/ctlamb/CaribouIPM_BCAB/f069f1f6f0705dc954a30a4cecbd9ff9bba7f2e3/"
    query = urllib.parse.urlencode({
        "service": "WFS", "version": "2.0.0", "request": "GetFeature",
        "typeNames": "pub:WHSE_WILDLIFE_INVENTORY.SPI_SURVEY_SUMMARIES_SV",
        "outputFormat": "application/json",
        "CQL_FILTER": "SPECIES_CODE='M-RATA' AND POPULATION_UNIT_NAME='Purcell Central'",
    })
    urls = {
        "pc.csv": "https://open.canada.ca/data/dataset/8d2849d9-a723-46c1-b94b-ed4a76e78195/resource/f9a392dc-aa09-41bd-ae74-c8de9ed5d42b/download/jasper_np_alpine_caribou_population_1988-2017_data.csv",
        "wsi_central.json": "https://openmaps.gov.bc.ca/geo/pub/ows?" + query,
        "counts.csv": git + "data/clean/counts.csv",
        "survival.csv": git + "data/clean/survival.csv",
        "dataprep.Rmd": git + "data/dataprep.Rmd",
        "zenodo_versions.json": "https://zenodo.org/api/records/10834654/versions",
    }
    manifest = {}
    for name, url in urls.items():
        data = (root / name).read_bytes()
        manifest[name] = {"url": url, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}

    # The second header is a French translation, not an observation.
    all_pc = list(csv.DictReader((root / "pc.csv").read_text(encoding="cp1252").splitlines()))
    assert all_pc[0]["Unique ID"] == "ID unique"
    pc = all_pc[1:]
    assert len({r["Unique ID"] for r in pc}) == len(pc)
    maligne = [r for r in pc if r["Region"] == "Maligne"]
    fields = list(pc[0])
    total_key = "Total number of individuals"
    classes = fields[8:]
    calves = fields[14:]
    groups = collections.defaultdict(list)
    duplicate_groups = collections.defaultdict(list)
    for row in maligne:
        key = (row["Survey type"], int(row["Year"]), int(row["Month"]), int(row["Day"]))
        groups[key].append(row)
        duplicate_groups[tuple(row[k] for k in fields[1:])].append(row["Unique ID"])
    flights = []
    for (kind, year, month, day), rows in sorted(groups.items()):
        flights.append({
            "type": kind, "date": f"{year:04d}-{month:02d}-{day:02d}",
            "record_ids": [r["Unique ID"] for r in rows],
            "sum_recorded_totals": sum(int(r[total_key]) for r in rows if r[total_key]),
            "missing_total_ids": [r["Unique ID"] for r in rows if not r[total_key]],
            "sum_recorded_calves": sum(int(r[k]) for r in rows for k in calves if r[k]),
            "component_sum_mismatch_ids": [r["Unique ID"] for r in rows if r[total_key]
                and sum(int(r[k]) for k in classes if r[k]) != int(r[total_key])],
        })

    wsi = json.loads((root / "wsi_central.json").read_text())
    properties = [f["properties"] for f in wsi["features"]] if isinstance(wsi, dict) else wsi
    keys = ["SURVEY_SUMMARY_DETAIL_ID", "SUMMARY_YEAR", "SUMMARY_MONTH", "SUMMARY_DAY",
            "PARAMETER_METHOD_CODE", "PARAMETER_METHOD_NAME", "PARAMETER_VALUE",
            "BEST_PARAMETER_VALUE", "SUMMARY_DETAIL_NOTE", "SUMMARY_GENERAL_NOTE"]
    individuals = sorted(
        [{k: r[k] for k in keys} for r in properties if r["PARAMETER_CODE"] == "Individuals"],
        key=lambda r: (r["SUMMARY_YEAR"], r["PARAMETER_METHOD_CODE"]))
    best = collections.Counter(r["SUMMARY_YEAR"] for r in individuals if r["BEST_PARAMETER_VALUE"] == "Yes")
    count_rows = list(csv.DictReader((root / "counts.csv").open()))
    survival_rows = list(csv.DictReader((root / "survival.csv").open()))
    target_herds = ["Maligne", "Purcells Central", "Banff"]
    counts = [{k: r[k] for k in ["herd", "year", "count", "Sightability", "sd", "MinUsed"]}
              for r in count_rows if r["herd"] in target_herds]
    survival = {herd: [r for r in survival_rows if r["herd"] == herd] for herd in target_herds}
    versions = json.loads((root / "zenodo_versions.json").read_text())["hits"]
    assert len(versions["hits"]) == versions["total"], "Version response is paginated: retrieve remaining pages"
    records = [{"record_id": r["id"], "version": r.get("metadata", {}).get("version"),
                "files": [{k: f[k] for k in ["key", "size", "checksum"]} for f in r.get("files", [])]}
               for r in versions["hits"]]
    return {
        "retrieved_date_hobart": "2026-10-14", "scope": "Descriptive source audit; no deduplication, fit or empirical test",
        "manifest": manifest,
        "parks_canada": {"data_rows": len(pc), "maligne_rows": len(maligne), "flights": flights,
            "identical_maligne_records_excluding_id": [ids for ids in duplicate_groups.values() if len(ids) > 1],
            "maligne_2014_records": [r for r in maligne if r["Year"] == "2014"],
            "blank_cell_policy": "Sums of recorded numeric components only. Agreement with totals is an arithmetic check, not certification that blank denotes zero."},
        "wsi": {"rows": len(properties), "secured_values": sorted({r["SECURED_IND"] for r in properties}),
            "individuals_rows": individuals, "years_with_multiple_best_values": sorted(y for y, n in best.items() if n > 1)},
        "archive_counts": counts, "archive_survival": survival,
        "zenodo": {"records": records, "file_bearing_records": sum(bool(r["files"]) for r in records),
            "distinct_file_checksums": sorted({f["checksum"] for r in records for f in r["files"]})},
        "banff_primary_text": {
            "doi": "10.1111/j.1523-1739.2009.01343.x",
            "url": "https://www.researchgate.net/publication/38024114_Revisiting_Extinction_in_National_Parks_Mountain_Caribou_in_Banff",
            "inspection": "Author-uploaded full text read in browser; not part of automated checks",
            "findings": ["Figure 1 and narrative date extirpation to April 2009; archive 2008 label remains unresolved",
                "Figure 1 caption describes aerial surveys, annual maximum counts and telemetry",
                "Text describes recovery actions commencing around 2002, including reduced elk numbers, deferred prescribed fires and reduced human impacts"]},
    }


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    result = audit(pathlib.Path(sys.argv[1]))
    pathlib.Path(sys.argv[2]).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"PC_rows": result["parks_canada"]["data_rows"],
                      "Maligne_flights": len(result["parks_canada"]["flights"]),
                      "WSI_rows": result["wsi"]["rows"],
                      "Zenodo_file_bearing_records": result["zenodo"]["file_bearing_records"]}))
