"""Bounded Haley artifact audit; reads peer files and rebuilds only in a temp dir.

Run from the repo with:
  uv run --offline --with matplotlib python analysis/astra/artifact_review_20261014/haley_checks.py
No fitting, inference, simulation, or new uncertainty intervals.
"""
import csv
import hashlib
import json
import math
from pathlib import Path
import runpy
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT / "analysis/fable/haley"
REF = ROOT / "analysis/astra/a_power_review/haley_source_excerpt.json"
OUT = Path(__file__).with_suffix(".json")
checks = []


def check(name, ok, details=None):
    checks.append({"name": name, "passed": bool(ok), "details": details})
    assert ok, name


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rows(path):
    with Path(path).open(newline="") as fh:
        return list(csv.DictReader(fh))


def textval(value):
    return "" if value is None else str(value)


source = json.loads((ART / "haley_source.json").read_text())
reference = json.loads(REF.read_text())
a7 = reference["appendix7_page110"]
a11 = reference["appendix11_page116"]
a12 = reference["appendix12_page117"]
check("primary PDF pin agrees with verified source receipt",
      source["source_sha256"] == reference["source_sha256"]
      and source["source_url"] == reference["source_url"])
cache = Path("/tmp/haley-review14/bryant1998.pdf")
if cache.is_file():
    check("cached primary PDF bytes match source pin", digest(cache) == source["source_sha256"])

maps = [
    ("appendix7_p110", a7, {
        "year": "year", "adults_age2plus": "adults_age2plus", "yearlings": "yearlings",
        "young_of_year": "young_of_year", "tagged_young_of_year_male": "tagged_male_young_of_year",
        "tagged_young_of_year_female": "tagged_female_young_of_year",
        "immigrants": "immigrants", "litters": "litters"}),
    ("appendix12_p117_nonpups", a12, {
        "transition_start": "transition_start_year", "tagged_exposed_n": "tagged_adults_and_yearlings",
        "tagged_survivors_s": "surviving_tagged_adults", "count_exposed_n": "adults_and_yearlings",
        "count_survivors_s": "apparent_survivors"}),
    ("appendix11_p116_pups", a11, {
        "transition_start": "transition_start_year", "tagged_exposed_n": "tagged_young_of_year",
        "tagged_survivors_s": "tagged_yearlings_next_year", "count_exposed_n": "total_young_of_year",
        "count_survivors_s": "apparent_survivors"}),
]
for section, ref, mapping in maps:
    check(section + " all source arrays agree", all(source[section][k] == ref[v] for k, v in mapping.items()),
          {"arrays": len(mapping), "values": sum(len(ref[v]) for v in mapping.values())})
for section, ref in (("appendix12_p117_nonpups", a12), ("appendix11_p116_pups", a11)):
    expected = [ref["printed_tagged_mean"], ref["printed_tagged_sd"], ref["printed_tagged_n_years"]]
    check(section + " printed summary agrees", source[section]["printed_tagged_mean_sd_years"] == expected)

raw = rows(ROOT / "data/raw/williams2021/population_data.csv")
wrows = [r for r in raw if r["ID"] == "15"]
check("unique Williams ID15 row", len(wrows) == 1)
wrow = wrows[0]
check("Williams ID15 species identity", "Marmota_vancouverensis" in wrow.values())
years = list(range(1981, 2001))
wtotal = [int(wrow[str(y)]) for y in years]
check("Williams all20 annual values read directly from raw CSV",
      source["williams_id15"]["year"] == years and source["williams_id15"]["total"] == wtotal)
totals = [sum(v) for v in zip(a7["adults_age2plus"], a7["yearlings"], a7["young_of_year"])]
check("ten source-overlap matches and retained1987 conflict",
      totals[0] == 18 and int(wrow["1987"]) == 28
      and all(v == int(wrow[str(y)]) for y, v in zip(a7["year"][1:], totals[1:])))

annual = rows(ART / "source_table_annual.csv")
check("annual CSV row count and ordering", [int(r["year"]) for r in annual] == years)
amap = {"adults_age2plus": "adults_age2plus", "yearlings": "yearlings", "young_of_year": "young_of_year",
        "tagged_yoy_male": "tagged_male_young_of_year", "tagged_yoy_female": "tagged_female_young_of_year",
        "immigrants": "immigrants", "litters": "litters"}
for r in annual:
    y = int(r["year"])
    assert int(r["williams_total"]) == int(wrow[str(y)])
    if y in a7["year"]:
        i = a7["year"].index(y)
        assert int(r["bryant_age_summed_total"]) == totals[i]
        assert all(r[k] == textval(a7[v][i]) for k, v in amap.items())
        assert "App. 7 p. 110" in r["source_note"]
    else:
        assert all(r[k] == "" for k in ["bryant_age_summed_total", *amap])
        assert "Williams only" in r["source_note"]
check("all annual CSV values and missing entries match independent reference/raw CSV", True)

transitions = rows(ART / "source_table_transitions.csv")
check("transition CSV has20 distinct cohort rows", len(transitions) == 20
      and len({(r["transition"], r["class"]) for r in transitions}) == 20)
for section, ref, mapping in maps[1:]:
    is_pup = section.startswith("appendix11")
    selected = [r for r in transitions if r["class"].startswith("pups" if is_pup else "non-pups")]
    for i, r in enumerate(selected):
        t = ref["transition_start_year"][i]
        assert r["transition"] == f"{t}->{t+1}"
        for key, refkey in mapping.items():
            if key != "transition_start":
                assert r[key] == textval(ref[refkey][i])
        assert ("App. 11 p. 116" if is_pup else "App. 12 p. 117") in r["source"]
check("all transition CSV values, start/end years, zero and null entries match reference", True)

summary = {
    "tagged_nonpup_n_s": [sum(a12["tagged_adults_and_yearlings"]), sum(a12["surviving_tagged_adults"])],
    "tagged_pup_n_s": [sum(a11["tagged_young_of_year"]), sum(v or 0 for v in a11["tagged_yearlings_next_year"])],
    "count_nonpup_n_s": [sum(a12["adults_and_yearlings"]), sum(a12["apparent_survivors"])],
    "count_pup_n_s": [sum(a11["total_young_of_year"]), sum(v or 0 for v in a11["apparent_survivors"])],
    "pups": sum(a7["young_of_year"]), "litters": sum(a7["litters"]),
    "litter_positive_years": sum(v > 0 for v in a7["litters"]),
    "litter_zero_years": [y for y, v in zip(a7["year"], a7["litters"]) if v == 0],
    "immigrants": sum(v or 0 for v in a7["immigrants"]),
}
check("narrative descriptive sums and8of11 litter years", summary == {
    "tagged_nonpup_n_s": [97, 64], "tagged_pup_n_s": [24, 11],
    "count_nonpup_n_s": [123, 83], "count_pup_n_s": [55, 30],
    "pups": 59, "litters": 17, "litter_positive_years": 8,
    "litter_zero_years": [1989, 1992, 1995], "immigrants": 9}, summary)
check("three numerical cross-table conflicts remain preserved",
      a11["apparent_survivors"][1] == 7 and a7["yearlings"][2] == 5
      and a12["surviving_tagged_adults"][7] == 10 and a7["adults_age2plus"][8] == 7
      and a11["tagged_young_of_year"][9] == 7
      and a7["tagged_male_young_of_year"][9] + a7["tagged_female_young_of_year"][9] == 4)

with tempfile.TemporaryDirectory(prefix="haley-qa-") as temp:
    temp = Path(temp)
    for name in ("make_haley.py", "haley_source.json"):
        shutil.copy2(ART / name, temp / name)
    module = runpy.run_path(str(temp / "make_haley.py"))
    module["write_tables"]()
    module["figure"]()
    figure = module["plt"].gcf()
    axes = figure.axes
    check("four rendered axes", len(axes) == 4)
    check("plotted Williams data match independent raw series",
          list(axes[0].lines[0].get_xdata()) == years and list(axes[0].lines[0].get_ydata()) == wtotal)
    check("plotted Bryant totals match source",
          list(axes[0].lines[1].get_xdata()) == a7["year"] and list(axes[0].lines[1].get_ydata()) == totals)
    check("all33 stage-bar heights match source arrays",
          all([p.get_height() for p in container] == a7[key]
              for container, key in zip(axes[1].containers, ["adults_age2plus", "yearlings", "young_of_year"])))
    actual = [(float(line.get_xdata()[0]), float(line.get_ydata()[0]))
              for line in axes[2].lines if len(line.get_xdata())]
    expected = [(t - .12, s/n) for t, s, n in zip(a12["transition_start_year"],
                a12["surviving_tagged_adults"], a12["tagged_adults_and_yearlings"])]
    expected += [(t + .12, s/n) for t, s, n in zip(a11["transition_start_year"],
                 a11["tagged_yearlings_next_year"], a11["tagged_young_of_year"]) if n]
    check("all15 plotted persistence points use s/n with correct cohort years and missing gaps",
          len(actual) == 15 and all(math.isclose(x, ex) and math.isclose(y, ey)
                                   for (x, y), (ex, ey) in zip(actual, expected)))
    labels = [label.get_text() for label in axes[2].texts]
    check("genuine zero and conflict labels retained", all(v in labels for v in ["0/3", "0/7‡", "10/15‡"]))
    check("persistence has no interval artists", not axes[2].containers and not axes[2].collections)
    check("all litter bars and10 recorded immigrant bars match source",
          [p.get_height() for p in axes[3].containers[0]] == a7["litters"]
          and [c[0].get_height() for c in axes[3].containers[1:]] == [v for v in a7["immigrants"] if v is not None]
          and any(t.get_text() == "n/a" and math.isclose(t.get_position()[0], 1987.18) for t in axes[3].texts))
    for name in ("source_table_annual.csv", "source_table_transitions.csv", "haley_case.png"):
        check("temporary rebuild byte match: " + name, digest(temp / name) == digest(ART / name))
    subprocess.run(["qpdf", "--check", str(ART / "haley_case.pdf")], check=True, capture_output=True)
    check("committed PDF passes qpdf syntax/stream check", True)
    for prefix, path in (("committed", ART / "haley_case.pdf"), ("rebuilt", temp / "haley_case.pdf")):
        subprocess.run(["pdftoppm", "-f", "1", "-singlefile", "-r", "100", "-png", str(path), str(temp / prefix)],
                       check=True, capture_output=True)
    check("temporary rebuild PDF raster byte match", digest(temp / "committed.png") == digest(temp / "rebuilt.png"))
    version = module["matplotlib"].__version__
    module["plt"].close(figure)

receipt = {
    "scope": "Source transcription, CSV and figure consistency; no empirical model or inference",
    "reviewed_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "matplotlib_version": version,
    "checks": checks,
    "all_checks_passed": all(c["passed"] for c in checks),
    "manual_review": "PNG and a180dpi rendering of the committed PDF were visually inspected; see review memo for interpretation/display corrections.",
    "source_independence_limit": "This verifies values against the previously source-checked Astra receipt; it does not independently establish how Fable performed re-extraction.",
    "input_sha256": {str(p.relative_to(ROOT)): digest(p) for p in [
        REF, ROOT / "data/raw/williams2021/population_data.csv", *sorted(ART.glob("*")),
        ROOT / "notes/haley_case_narrative_20261014.md"] if p.is_file()},
}
OUT.write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps({"checks": len(checks), "all_passed": receipt["all_checks_passed"], "receipt": str(OUT)}, indent=2))
