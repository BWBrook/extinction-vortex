"""Caribou descriptive deep dive (Banff, Maligne, Purcells Central): source crosswalk tables and a small-multiples
figure from pinned public snapshots. Descriptive tabulation of source rows only: no fitting, imputation,
deduplication or new interval. Run: uv run --with matplotlib python make_caribou.py SOURCE_DIR
SOURCE_DIR holds the files listed in caribou_sources.json (download URLs and SHA-256 recorded there)."""
import collections, csv, hashlib, json, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1]
MAN = json.load(open(os.path.join(HERE, "caribou_sources.json")))
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
OBS, MNKA, MC = "#2a78d6", "#eb6834", "#1baf7a"
WILLIAMS_REPO = os.path.join(HERE, "..", "..", "..", "data", "raw", "williams2021", "population_data.csv")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def read(name, enc="utf-8"):
    return list(csv.DictReader(open(os.path.join(SRC, name), encoding=enc)))


def check_hashes():
    out = {}
    for f, m in MAN["files"].items():
        h = sha(os.path.join(SRC, f)); out[f] = h
        if h != m["sha256_fable"]:
            raise SystemExit(f"{f}: snapshot hash {h} differs from the recorded {m['sha256_fable']}")
    return out


def williams():
    rows = {r["ID"]: r for r in csv.DictReader(open(WILLIAMS_REPO, encoding="utf-8"))}
    return {i: {int(y): int(float(rows[i][y])) for y in rows[i] if y.isdigit() and rows[i][y] not in ("NULL", "")} for i in ("27", "28")}


def lamb(herd, f="counts.csv"):
    return [r for r in read(f) if r["herd"] == herd]


def write(name, header, rows):
    with open(os.path.join(HERE, name), "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n"); w.writerow(header); w.writerows(rows)


def maligne(W):
    pc = list(csv.DictReader(open(os.path.join(SRC, "pc.csv"), encoding="cp1252").read().splitlines()))
    assert pc[0]["Unique ID"] == "ID unique"            # second header row is a French translation
    pc = [r for r in pc[1:] if r["Region"] == "Maligne"]
    fall = collections.defaultdict(list)
    for r in pc:
        if r["Survey type"] == "rut":
            fall[int(r["Year"])].append(r)
    lc = {int(r["year"]): int(r["count"]) for r in lamb("Maligne")}
    years = sorted(set(fall) | set(lc) | set(W["27"]))
    out = []
    for y in years:
        g = fall.get(y, [])
        tot = [int(r["Total number of individuals"]) for r in g if r["Total number of individuals"]]
        miss = [r["Unique ID"] for r in g if not r["Total number of individuals"]]
        dates = sorted({f"{int(r['Year']):04d}-{int(r['Month']):02d}-{int(r['Day']):02d}" for r in g})
        note = []
        if y == 2014: note.append("groups 423/424 (28 Oct) identical composition, different locations; not deduplicated")
        if miss: note.append(f"record(s) {','.join(miss)} with blank total and composition fields")
        if y in W["27"] and y in lc and W["27"][y] != lc[y]: note.append("Williams differs from Lamb archive")
        out.append([y, ";".join(dates), len(g), sum(tot) if g else "", ";".join(miss), lc.get(y, ""), W["27"].get(y, ""), "; ".join(note)])
    write("maligne_census.csv", ["year", "parks_fall_flight_dates", "parks_fall_group_records", "parks_fall_sum_recorded_totals",
                                 "parks_blank_total_ids", "lamb_archive_count", "williams_id27", "notes"], out)
    return out


def purcells():
    w = json.load(open(os.path.join(SRC, "wsi_central.json")))
    props = [f["properties"] for f in (w["features"] if isinstance(w, dict) else w)]
    ind = [p for p in props if p.get("PARAMETER_NAME") == "Individuals"]
    by = collections.defaultdict(dict)
    for p in sorted(ind, key=lambda p: p["SURVEY_SUMMARY_DETAIL_ID"]):
        k = p["PARAMETER_METHOD_CODE"]; y = p["SUMMARY_YEAR"]
        cell = by[y].setdefault(k, [])
        cell.append((p["PARAMETER_VALUE"], p["BEST_PARAMETER_VALUE"], p["SURVEY_SUMMARY_DETAIL_ID"],
                     f"{y:04d}-{p['SUMMARY_MONTH'] or 0:02d}-{p['SUMMARY_DAY'] or 0:02d}", (p.get("SUMMARY_DETAIL_NOTE") or "").strip()))
    lc = {int(r["year"]): int(r["count"]) for r in lamb("Purcells Central")}
    out = []
    for y in sorted(set(by) | set(lc)):
        cells = by.get(y, {})
        f = lambda k: ";".join(str(v[0]) for v in cells.get(k, []))
        best = ";".join(f"{k}" for k in ("OTC", "MNKA", "MC") for v in cells.get(k, []) if v[1] == "Yes")
        ids = ";".join(str(v[2]) for k in ("OTC", "MNKA", "MC") for v in cells.get(k, []))
        dates = ";".join(sorted({v[3] for k in cells for v in cells[k]}))
        notes = " | ".join(sorted({v[4] for k in cells for v in cells[k] if v[4]}))
        out.append([y, dates, f("OTC"), f("MNKA"), f("MC"), best, ids, lc.get(y, ""), notes])
    write("purcells_central_census.csv", ["year", "wsi_survey_dates", "wsi_OTC", "wsi_MNKA", "wsi_MC", "wsi_best_flagged",
                                          "wsi_detail_ids", "lamb_archive_count", "wsi_detail_notes"], out)
    return out


def banff(W):
    lc = {int(r["year"]): int(r["count"]) for r in lamb("Banff")}
    out = [[y, W["28"].get(y, ""), lc.get(y, ""), "match" if W["28"].get(y) == lc.get(y) else "DIFFERS",
            "archive/Williams terminal zero labelled 2008; primary paper dates the last five deaths to the April 2009 avalanche (unresolved)"
            if y == 2008 else ""] for y in sorted(set(lc) | set(W["28"]))]
    write("banff_census.csv", ["year", "williams_id28", "lamb_archive_count", "crosswalk", "notes"], out)
    return out


def demography():
    out = []
    for h in ("Maligne", "Purcells Central", "Banff"):
        for r in lamb(h, "survival.csv"):
            out.append([h, r["year"], "adult female annual survival (archive survival.csv)", r["est"], f"sd {float(r['sd']):.3f}",
                        "herd-year aggregate; KM at month 12 with staggered entry, boundary values by resampling (dataprep.Rmd); "
                        "not a binomial denominator or recovered CI; collar risk sets not in the release"])
        for r in lamb(h, "recruitment_counts.csv"):
            out.append([h, r["year"], f"calves / classified non-calves ({r['season']}, {r['type']}; archive recruitment_counts.csv)",
                        f"{r['calves']}/{r['adults']}", "",
                        "shared-survey composition; denominator excludes unclassified animals; not automatically calf:cow"])
    write("demographic_evidence.csv", ["herd", "year", "quantity", "value", "uncertainty_as_given", "provenance"], out)
    return out


def figure(ml, pu, bf):
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                         "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": SURF, "axes.facecolor": SURF})
    fig, ax = plt.subplots(3, 1, figsize=(7.2, 8.6), sharex=True)
    dem = demography()
    for a in ax:
        a.grid(axis="y", color=GRID, linewidth=0.6); a.set_axisbelow(True); a.set_xlim(1984.5, 2022.5)

    def rug(a, herd, ytop):
        sv = sorted({int(r[1]) for r in dem if r[0] == herd and r[2].startswith("adult female")})
        rc = sorted({int(r[1]) for r in dem if r[0] == herd and r[2].startswith("calves")})
        a.plot(sv, [-0.06 * ytop] * len(sv), linestyle="none", marker="|", markersize=9, color=INK, label="survival estimate year")
        a.plot(rc, [-0.12 * ytop] * len(rc), linestyle="none", marker="|", markersize=9, color=INK2, label="composition survey year")

    # Maligne
    a = ax[0]; top = 72
    a.plot([r[0] for r in ml if r[5] != ""], [r[5] for r in ml if r[5] != ""], color=INK2, linewidth=1.6, label="Lamb archive count")
    a.plot([r[0] for r in ml if r[3] != ""], [r[3] for r in ml if r[3] != ""], linestyle="none", marker="o", markersize=5, color=OBS,
           label="Parks Canada fall group sum (minimum count)")
    a.plot([r[0] for r in ml if r[6] != ""], [r[6] for r in ml if r[6] != ""], linestyle="none", marker="s", markersize=5,
           markerfacecolor="none", markeredgecolor=INK, label="Williams ID 27")
    rug(a, "Maligne", top)
    a.annotate("2006–12: Williams ≠ archive", xy=(2009, 7), xytext=(2005.5, 30), fontsize=7.5, color=INK,
               arrowprops={"arrowstyle": "-", "color": INK2, "linewidth": 0.8})
    a.set_ylim(-0.17 * top, top); a.set_ylabel("Animals")
    a.set_title("(a) Maligne (Jasper NP)", loc="left", fontsize=9.5, color=INK)
    a.legend(loc="upper right", frameon=False, fontsize=7.5)

    # Purcells Central
    a = ax[1]; top = 20
    a.plot([r[0] for r in pu if r[7] != ""], [r[7] for r in pu if r[7] != ""], color=INK2, linewidth=1.6, label="Lamb archive count")
    for col, k, mk, lab in ((2, "OTC", "o", "WSI observed total count (OTC)"), (3, "MNKA", "^", "WSI minimum known alive (MNKA)"),
                            (4, "MC", "D", "WSI model/correction (MC)")):
        pts = [(r[0], float(v)) for r in pu if r[col] != "" for v in str(r[col]).split(";")]
        a.plot([p[0] + {2: -0.18, 3: 0, 4: 0.18}[col] for p in pts], [p[1] for p in pts], linestyle="none", marker=mk, markersize=5,
               color={2: OBS, 3: MNKA, 4: MC}[col], label=lab)
    rug(a, "Purcells Central", top)
    a.annotate("1997: OTC 2, MNKA 14", xy=(1997, 2), xytext=(1999.5, 15.5), fontsize=7.5, color=INK,
               arrowprops={"arrowstyle": "-", "color": INK2, "linewidth": 0.8})
    a.set_ylim(-0.17 * top, top); a.set_ylabel("Animals")
    a.set_title("(b) Purcells Central (BC)", loc="left", fontsize=9.5, color=INK)
    a.legend(loc="upper right", frameon=False, fontsize=7.5)

    # Banff
    a = ax[2]; top = 32
    a.plot([r[0] for r in bf if r[2] != ""], [r[2] for r in bf if r[2] != ""], color=INK2, linewidth=1.6, marker="o", markersize=4,
           markerfacecolor=SURF, label="Lamb archive count = Williams ID 28 (16/16)")
    for x, lab, ha, dx, yy in ((2002, "c. 2002: recovery actions\n(elk reduction, fire deferral)", "right", -0.3, 0.80),
                               (2009.3, "Apr 2009: avalanche kills\nlast five animals", "left", 0.3, 0.55)):
        a.axvline(x, color=INK2, linewidth=0.8, linestyle=(0, (3, 3)))
        a.text(x + dx, top * yy, lab, fontsize=7.5, color=INK, va="top", ha=ha)
    a.annotate("archive zero labelled 2008", xy=(2008, 0), xytext=(2011.2, 5.5), fontsize=7, color=INK2,
               arrowprops={"arrowstyle": "-", "color": INK2, "linewidth": 0.8})
    a.set_ylim(-0.17 * top, top); a.set_ylabel("Animals")
    a.set_title("(c) Banff (Banff NP)", loc="left", fontsize=9.5, color=INK)
    a.legend(loc="upper right", frameon=False, fontsize=7.5)
    a.set_xlabel("Year")
    fig.text(0.01, 0.004, "Rugs below zero mark years with an archived survival estimate (black) or composition survey (grey); none for Banff.\n"
             "Sources: Parks Canada open data; BC WSI; Lamb et al. 2024 archive (f069f1f6); Williams et al. 2021; Hebblewhite et al. 2010. "
             "Descriptive only.", fontsize=7, color=INK2)
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(HERE, f"caribou_case.{ext}"), dpi=200)


if __name__ == "__main__":
    hashes = check_hashes()
    W = williams()
    ml, pu, bf = maligne(W), purcells(), banff(W)
    figure(ml, pu, bf)
    print("hashes ok:", sorted(hashes))
    print("Banff crosswalk:", sum(r[3] == "match" for r in bf), "of", len(bf))
