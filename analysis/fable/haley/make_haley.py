"""Haley Lake descriptive deep dive: source table and case figure from haley_source.json (no fitting,
no intervals). Run: uv run --with matplotlib python make_haley.py"""
import csv, json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(HERE, "haley_source.json")))
W, A7, A12, A11 = S["williams_id15"], S["appendix7_p110"], S["appendix12_p117_nonpups"], S["appendix11_p116_pups"]

SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
ADULT, YEARL, PUP, LITTER, IMM = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"


def write_tables():
    w = dict(zip(W["year"], W["total"])); a = {y: i for i, y in enumerate(A7["year"])}
    with open(os.path.join(HERE, "source_table_annual.csv"), "w", newline="") as fh:
        c = csv.writer(fh, lineterminator="\n")
        c.writerow(["year", "williams_total", "bryant_age_summed_total", "adults_age2plus", "yearlings", "young_of_year",
                    "tagged_yoy_male", "tagged_yoy_female", "immigrants", "litters", "source_note"])
        for y in W["year"]:
            if y in a:
                i = a[y]; tot = A7["adults_age2plus"][i] + A7["yearlings"][i] + A7["young_of_year"][i]
                note = "Bryant App. 7 p. 110; " + ("CONFLICT: 18 vs Williams 28" if y == 1987 else "matches Williams")
                c.writerow([y, w[y], tot, A7["adults_age2plus"][i], A7["yearlings"][i], A7["young_of_year"][i],
                            A7["tagged_young_of_year_male"][i], A7["tagged_young_of_year_female"][i],
                            "" if A7["immigrants"][i] is None else A7["immigrants"][i], A7["litters"][i], note])
            else:
                c.writerow([y, w[y], "", "", "", "", "", "", "", "", "Williams only; no recovered source"])
    with open(os.path.join(HERE, "source_table_transitions.csv"), "w", newline="") as fh:
        c = csv.writer(fh, lineterminator="\n")
        c.writerow(["transition", "class", "tagged_exposed_n", "tagged_survivors_s", "count_exposed_n", "count_survivors_s", "source"])
        for k, t in enumerate(A12["transition_start"]):
            c.writerow([f"{t}->{t + 1}", "non-pups (adults+yearlings -> adults 2+)", A12["tagged_exposed_n"][k], A12["tagged_survivors_s"][k],
                        A12["count_exposed_n"][k], A12["count_survivors_s"][k], "Bryant App. 12 p. 117"])
        for k, t in enumerate(A11["transition_start"]):
            sv = A11["tagged_survivors_s"][k]; cs = A11["count_survivors_s"][k]
            c.writerow([f"{t}->{t + 1}", "pups (young-of-year -> yearlings)", A11["tagged_exposed_n"][k], "" if sv is None else sv,
                        A11["count_exposed_n"][k], "" if cs is None else cs, "Bryant App. 11 p. 116"])


def figure():
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                         "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                         "figure.facecolor": SURF, "axes.facecolor": SURF})
    fig, ax = plt.subplots(4, 1, figsize=(7.2, 9.4), sharex=True, gridspec_kw={"height_ratios": [1.15, 1, 1, 0.8]})
    yrs = W["year"]
    for a in ax:
        a.grid(axis="y", color=GRID, linewidth=0.6); a.set_axisbelow(True)
        a.set_xlim(1980.4, 2000.6)

    # (a) abundance
    a = ax[0]
    a.axvspan(1987.5, 1997.5, color="#f0efec", zorder=0)
    a.text(1992.5, 35.2, "Bryant (1998) totals match Williams, 1988–1997", ha="center", va="top", color=INK2, fontsize=8)
    a.plot(yrs, W["total"], color=INK2, linewidth=2, marker="o", markersize=5, markerfacecolor=SURF, label="Williams ID 15")
    btot = [x + y + z for x, y, z in zip(A7["adults_age2plus"], A7["yearlings"], A7["young_of_year"])]
    a.plot(A7["year"], btot, linestyle="none", marker="s", markersize=4.5, color=INK, label="Bryant App. 7 (age-summed)")
    a.annotate("1987: Williams 28,\nBryant 18 (unresolved)", xy=(1987, 18), xytext=(1983.2, 7), fontsize=8, color=INK,
               arrowprops={"arrowstyle": "-", "color": INK2, "linewidth": 0.8})
    for x0, x1 in ((1981, 1986), (1998, 2000)):
        a.text((x0 + x1) / 2, 37.5, "Williams only", ha="center", va="top", color=INK2, fontsize=7.5, style="italic")
    a.set_ylim(0, 38); a.set_ylabel("Animals counted")
    a.set_title("(a) Annual count (seasonal age-class maxima summed)", loc="left", fontsize=9.5, color=INK)
    a.legend(loc="upper right", bbox_to_anchor=(1.0, 0.82), frameon=False, fontsize=8)

    # (b) stage composition
    a = ax[1]; bottom = [0] * len(A7["year"])
    for key, col, lab in (("adults_age2plus", ADULT, "Adults (age 2+)"), ("yearlings", YEARL, "Yearlings"),
                          ("young_of_year", PUP, "Pups (young-of-year)")):
        a.bar(A7["year"], A7[key], bottom=bottom, color=col, width=0.72, edgecolor=SURF, linewidth=1.5, label=lab)
        bottom = [b + v for b, v in zip(bottom, A7[key])]
    a.set_ylabel("Animals (seasonal max)")
    a.set_title("(b) Stage composition, Bryant App. 7 (1987–1997 only)", loc="left", fontsize=9.5, color=INK)
    a.legend(loc="upper left", frameon=False, fontsize=8, ncol=3)
    a.set_ylim(0, 31)

    # (c) tagged persistence, s/n by transition start; gaps where n = 0
    a = ax[2]
    for t, n, s in zip(A12["transition_start"], A12["tagged_exposed_n"], A12["tagged_survivors_s"]):
        a.plot(t - 0.12, s / n, marker="o", markersize=7, color=ADULT, markeredgecolor=SURF, markeredgewidth=1.2, linestyle="none")
        a.text(t - 0.12, s / n + 0.07, f"{s}/{n}" + ("‡" if t == 1994 else ""), ha="center", fontsize=7, color=INK)
    for t, n, s in zip(A11["transition_start"], A11["tagged_exposed_n"], A11["tagged_survivors_s"]):
        if n:
            a.plot(t + 0.12, s / n, marker="s", markersize=7, color=PUP, markeredgecolor=SURF, markeredgewidth=1.2, linestyle="none")
            a.text(t + 0.36, s / n - 0.09, f"{s}/{n}" + ("‡" if t == 1996 else ""), ha="left", va="center", fontsize=7, color=INK)
    a.plot([], [], marker="o", color=ADULT, linestyle="none", label="Tagged non-pups → adults (App. 12)")
    a.plot([], [], marker="s", color=PUP, linestyle="none", label="Tagged pups → yearlings (App. 11)")
    a.set_ylim(-0.5, 1.22); a.set_yticks([0, 0.5, 1])
    a.set_ylabel("Persistence s/n")
    a.set_title("(c) Tagged persistence by transition t → t+1 (minimum persistence; no intervals)", loc="left", fontsize=9.5, color=INK)
    a.legend(loc="lower center", frameon=False, fontsize=8, ncol=2)

    # (d) litters and recorded immigrants
    a = ax[3]
    a.bar([y - 0.18 for y in A7["year"]], A7["litters"], width=0.36, color=LITTER, edgecolor=SURF, linewidth=1.5, label="Litters")
    for y, v in zip(A7["year"], A7["litters"]):
        a.text(y - 0.18, v + 0.15, str(v), ha="center", fontsize=7, color=INK)
    for y, v in zip(A7["year"], A7["immigrants"]):
        if v is None:
            a.text(y + 0.18, 0.15, "n/a", ha="center", fontsize=7, color=INK2, style="italic")
        else:
            a.bar(y + 0.18, v, width=0.36, color=IMM, edgecolor=SURF, linewidth=1.5)
            a.text(y + 0.18, v + 0.15, str(v), ha="center", fontsize=7, color=INK)
    a.set_ylim(0, 5.2); a.set_ylabel("Count per year")
    a.set_title("(d) Litters and recorded immigrants, Bryant App. 7", loc="left", fontsize=9.5, color=INK)
    a.legend(handles=[Patch(color=LITTER, label="Litters"), Patch(color=IMM, label="Recorded immigrants (n/a = blank in source)")],
             loc="upper right", frameon=False, fontsize=8, ncol=2)
    a.set_xticks(range(1981, 2001, 2)); a.set_xlabel("Year (panel c: transition start year)")

    fig.text(0.01, 0.005, "‡ conflicts with Appendix 7 (see conflict register). Source: Bryant 1998 (UVic PhD), Apps 7, 11, 12; "
             "Williams et al. 2021 ID 15. Descriptive only.", fontsize=7, color=INK2)
    fig.tight_layout(rect=(0, 0.015, 1, 1))
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(HERE, f"haley_case.{ext}"), dpi=200)


if __name__ == "__main__":
    write_tables(); figure()
