#!/usr/bin/env python3
"""Bounded public-source inventory and count crosswalk; no inference or fitting."""
import argparse
import collections
import csv
import hashlib
import io
import json
from pathlib import Path
import urllib.request

COMMIT = "f069f1f6f0705dc954a30a4cecbd9ff9bba7f2e3"
RAW = f"https://raw.githubusercontent.com/ctlamb/CaribouIPM_BCAB/{COMMIT}/"
PAL = "https://pallter-data.marine.rutgers.edu/erddap/tabledap/"
EXPECTED = {
    "data/clean/counts.csv": "43c3e55ad82fe70783e417c39f2e7ff27f33fa9657a846f409a138f59dc40629",
    "data/clean/survival.csv": "d45a4fc39d579c2e0815671910567073ce9e7212e03109e81447beba4e7748da",
    "data/clean/recruitment_counts.csv": "1784440c7664205e71f68bbf312579ef4a8cd0422682111e166ae73f63a8ac68",
    "AdeliePenguinCensus.csv": "b4ef04e2275ea779fc8fe54fa13528dc2052d37dd88a60c811d54c7601f67b16",
    "AdeliePenguinAdultandChickCounts.csv": "40485a328af51727e019c2cd99e4795c098499fef86a9d4b2af435a6de5373e0",
    "AdeliePenguinBandsSeen.csv": "8e72cff0cdc8a9b31bbfaf4b8aa59f4ec982937ca0d9010c3f43caf58b7840ff",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, default=Path("/tmp/option3_phase2_audit"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[3]
    provenance = {}

    def get(name, url):
        path = args.cache_dir / name
        cached = path.exists() and not args.refresh
        if not cached:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(urllib.request.urlopen(url, timeout=40).read())
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        provenance[name] = {"url": url, "sha256": digest, "bytes": len(data)}
        if name in EXPECTED and digest != EXPECTED[name]:
            raise ValueError(f"Source changed since audit: {name}; do not silently reuse the conclusions")
        return data

    tables = {}
    for name in EXPECTED:
        is_pal = name.startswith("Adelie")
        data = get(name, PAL + name if is_pal else RAW + name)
        rows = list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))
        tables[name] = rows[1:] if is_pal else rows  # ERDDAP has a units row.

    tree_url = f"https://api.github.com/repos/ctlamb/CaribouIPM_BCAB/git/trees/{COMMIT}?recursive=1"
    tree = json.loads(get("github_tree.json", tree_url))
    assert not tree["truncated"], "An incomplete tree cannot establish absence"
    ignored = get("github_gitignore.txt", RAW + ".gitignore").decode().splitlines()
    counts = tables["data/clean/counts.csv"]
    herds = ["Maligne", "Purcells Central", "Banff", "George Mountain", "South Selkirks",
             "Purcells South", "Klinse-Za", "Quintette", "Quintette Full", "Burnt Pine", "Monashee"]
    overlap = {}
    for herd in herds:
        overlap[herd] = {}
        for name in ("counts", "survival", "recruitment_counts"):
            rows = [r for r in tables[f"data/clean/{name}.csv"] if r["herd"] == herd]
            years = sorted({int(r["year"]) for r in rows})
            item = {"rows": len(rows), "years": years}
            if name == "counts":
                assert len(years) == len(rows), f"Multiple census rows per year need adjudication: {herd}"
                item["values"] = {r["year"]: float(r["count"]) for r in rows}
                item["zero_years"] = sorted(int(r["year"]) for r in rows if float(r["count"]) == 0)
            overlap[herd][name] = item

    wp = repo / "data/raw/williams2021/population_data.csv"
    wb = wp.read_bytes()
    williams = {r["ID"]: r for r in csv.DictReader(io.StringIO(wb.decode()))}

    def compare(series_id, proposed_name, proposed):
        observed = {int(y): float(v) for y, v in williams[series_id].items()
                    if y.isdigit() and v not in ("NULL", "")}
        mismatches = [{"year": y, "Williams": n, "other": proposed.get(y)}
                      for y, n in observed.items() if proposed.get(y) != n]
        return {"proposed_crosswalk": proposed_name, "n_Williams": len(observed),
                "all_year_counts_equal": not mismatches, "mismatches": mismatches,
                "identity_status": "numerical crosswalk only; original source mapping not established"}

    crosswalks = {}
    for series_id, herd in [("27", "Maligne"), ("28", "Banff")]:
        series = {int(r["year"]): float(r["count"]) for r in counts if r["herd"] == herd}
        crosswalks[series_id] = compare(series_id, herd, series)

    census_keys = [(r['study_name'], r['island_name'], r['colony_code'])
                   for r in tables['AdeliePenguinCensus.csv']]
    assert len(census_keys) == len(set(census_keys)), 'Repeated colony census rows need adjudication before summing'
    lit = collections.defaultdict(float)
    for row in tables["AdeliePenguinCensus.csv"]:
        if row["island_name"] == "LIT":
            lit[row["study_name"]] += float(row["num_breeding_pairs"])
    calendar = {1900 + int(k[3:5]) if int(k[3:5]) >= 91 else 2000 + int(k[3:5]): v
                for k, v in lit.items()}
    crosswalks["25"] = compare("25", "Litchfield island sum; season start year", calendar)
    bands = tables["AdeliePenguinBandsSeen.csv"]
    output = {
        "audit": "bounded inventory/count comparison; not inference or original-source identity proof",
        "caribou_commit": COMMIT,
        "source_provenance": provenance,
        "Williams_sha256": hashlib.sha256(wb).hexdigest(),
        "github_tree": {"entries": len(tree["tree"]), "truncated": tree["truncated"],
                        "raw_paths": [r["path"] for r in tree["tree"] if r["path"].startswith("data/raw")],
                        "gitignore_excludes_data_raw": "data/raw" in ignored},
        "caribou_overlap": overlap,
        "Williams_crosswalks": crosswalks,
        "Palmer": {
            "row_counts": {k: len(v) for k, v in tables.items() if k.startswith("Adelie")},
            "Litchfield_pair_totals_by_season": dict(lit),
            "band_unique_ids": len({r["band_number"] for r in bands}),
            "resightings_by_island": dict(collections.Counter(r["island_name"] for r in bands)),
            "Litchfield_resighting_seasons": sorted({r["study_name"] for r in bands if r["island_name"] == "LIT"}),
            "observed_band_year_values": sorted({r["year"] for r in bands}),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(f"Wrote {args.output}; all six source hashes match the inspected audit inputs")


if __name__ == "__main__":
    main()
