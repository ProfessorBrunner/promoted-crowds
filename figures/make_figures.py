#!/usr/bin/env python3
"""Rebuild CROWD-1 figures F1-F4 (PDF + PNG) from the data files in figures/data/.

Self-contained: needs only numpy and matplotlib.  Reads nothing but the CSV/JSON in
figures/data/, so it reproduces the published figures without re-running any
simulation.  The one series that is simulated rather than read, F3's agent
trajectories, is produced by figures/gen_p6A_traces.py and committed as
figures/data/F3_P6A_agent.csv.

Paper numbering (owner-directed):
    F1  order advantage vs seed delay          (P1-delay; Stage 2 + Stage 2B task 1)
    F2  outbreak probability by campaign order (P1 and P2; Stage 2)
    F3  P6 case A activity trajectory          (Stage 2 P6 + Stage 2B task 3 solver)
    F4  onset, class 2 and class 1             (Stage 2 P4 + Stage 2B task 2 + P5)

Usage:  python figures/make_figures.py [--outdir DIR]
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402
import numpy as np                        # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

GREY = "#888888"
C_A, C_B, C_C, C_D = "#1f6fb4", "#b4531f", "#6a8f3c", "#8a4fa8"


def apply_style():
    """House style: open frame, small type, no grid.  Kept local so this script has
    no dependency beyond matplotlib."""
    plt.rcParams.update({
        "figure.dpi": 120, "savefig.dpi": 300,
        "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 7,
        "xtick.labelsize": 6, "ytick.labelsize": 6, "legend.fontsize": 6,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.linewidth": 0.8, "xtick.major.width": 0.8, "ytick.major.width": 0.8,
        "xtick.major.size": 3, "ytick.major.size": 3,
        "lines.solid_capstyle": "round", "legend.frameon": False,
        "axes.grid": False, "savefig.bbox": "tight", "pdf.fonttype": 42,
    })


def set_frame(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def panel_letter(ax, letter, dx=-0.175, dy=1.02):
    ax.text(dx, dy, letter, transform=ax.transAxes, fontweight="bold",
            fontsize=9, va="bottom", ha="left")


def read_csv(name):
    with open(os.path.join(DATA, name), newline="") as fh:
        return list(csv.DictReader(fh))


def read_table(name):
    return np.genfromtxt(os.path.join(DATA, name), delimiter=",", names=True)


def save(fig, outdir, stem):
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(outdir, f"{stem}.{ext}"), bbox_inches="tight")
    print(f"  wrote {stem}.pdf and {stem}.png", flush=True)


# ------------------------------------------------------------------ F1
def fig1(outdir):
    rows = read_csv("F1_measured.csv")
    cur = read_table("F1_exact_curves.csv")
    tm = float(rows[0]["t_multiplier_df23"])
    x2 = float(rows[0]["stationary_ratio_1_plus_x2"]) - 1.0
    g = lambda k: np.array([float(r[k]) for r in rows])          # noqa: E731

    fig, ax = plt.subplots(figsize=(4.4, 3.4))
    ax.plot(cur["tau0"], cur["ratio_time_dependent_exact"], color=C_A, lw=1.5, zorder=3)
    ax.plot(cur["tau0"], cur["ratio_frozen_proxy_exact"], color=C_B, lw=1.3, ls="--",
            zorder=2)
    ax.errorbar(g("tau0"), g("ratio_timedep_measured"),
                yerr=tm * g("ratio_timedep_sem"), fmt="o", ms=4.2, color=C_A,
                capsize=2, lw=1.0, ls="none", zorder=5,
                label="time-dependent ratio of $E\\,Z_1$")
    ax.errorbar(g("tau0"), g("ratio_frozen_measured"),
                yerr=tm * g("ratio_frozen_sem"), fmt="s", ms=3.8, mfc="white",
                mec=C_B, ecolor=C_B, capsize=2, lw=1.0, ls="none", zorder=4,
                label="frozen orientation-susceptibility proxy")
    ax.axhline(1.0 + x2, color=GREY, lw=0.7, ls=":", zorder=1)
    ax.text(7.9, 1.0 + x2 - 0.030, f"$1+x_2={1 + x2:.4f}$", va="top", ha="center",
            fontsize=6, color=GREY)
    ax.axhline(1.0, color=GREY, lw=0.5, ls=":", zorder=1)
    ax.text(5.4, 1.60, "time-dependent ratio of $E\\,Z_1$", fontsize=7, color=C_A,
            ha="center")
    ax.text(3.5, 1.27, "frozen orientation-susceptibility proxy\n"
            "$1+x_2(1-e^{-\\rho\\tau_0})$", fontsize=7,
            color=C_B, ha="center")
    ax.annotate("proxy ratio exactly 1", xy=(0.0, 1.0), xytext=(1.1, 1.055),
                fontsize=6, color=C_B, ha="left",
                arrowprops=dict(arrowstyle="-", lw=0.6, color=C_B))
    ax.text(0.975, 0.30,
            r"$\rho=\varepsilon=1$, $\lambda=2$, $N=10^5$;  $L=\ln 2$"
            "\n24 backgrounds $\\times$ $10^4$ seed trials"
            f"\nerror bars $t_{{0.975,23}}={tm:.3f}\\times$sem",
            transform=ax.transAxes, va="top", ha="right", fontsize=5.6, color="0.30")
    ax.set_xlabel(r"seed delay  $\tau_0$   (units of $\rho^{-1}=\varepsilon^{-1}$)")
    ax.set_ylabel("between-order ratio")
    ax.set_xlim(-0.35, 10.4)
    ax.set_ylim(0.93, 2.06)
    set_frame(ax)
    ax.legend(loc="lower right", bbox_to_anchor=(1.0, 0.0), fontsize=5.4,
              handlelength=1.6, borderaxespad=0.2, labelspacing=0.5)
    fig.tight_layout()
    save(fig, outdir, "F1_order_advantage_vs_delay")
    plt.close(fig)


# ------------------------------------------------------------------ F2
def fig2(outdir):
    rows = read_csv("F2_outbreak_probability.csv")
    p1 = [r for r in rows if r["prediction"] == "P1"]
    big = [r for r in rows if r["prediction"] == "P1 (N=1e6)"]
    p2 = [r for r in rows if r["prediction"] == "P2"]

    def err(rs):
        lo = [max(0.0, float(r["p_outbreak"]) - float(r["ci_lo"])) for r in rs]
        hi = [max(0.0, float(r["ci_hi"]) - float(r["p_outbreak"])) for r in rs]
        return [lo, hi]

    fig, (axa, axb) = plt.subplots(1, 2, figsize=(6.6, 3.15),
                                   gridspec_kw=dict(width_ratios=[1.35, 1.0]))
    groups = [("(40, 50, 140)", "o", "-", C_A, "$(40,50,140)$"),
              ("(40, 140, 50)", "o", "-", C_B, "$(40,140,50)$"),
              ("(50, 40, 140) (held out)", "^", "none", C_C, "$(50,40,140)$"),
              ("(140, 40, 50) (held out)", "v", "none", C_D, "$(140,40,50)$")]
    for name, mk, ls, col, lab in groups:
        rs = [r for r in p1 if r["order"] == name]
        if not rs:
            continue
        xs = [float(r["lam"]) for r in rs]
        ys = [float(r["p_outbreak"]) for r in rs]
        if len(rs) > 1:
            axa.plot(xs, ys, ls=ls, color=col, lw=1.1, zorder=2)
        axa.errorbar(xs, ys, yerr=err(rs), fmt=mk, ms=4.4, color=col, capsize=2,
                     lw=1.0, ls="none", zorder=4, label=lab)
    star = [r for r in big if r["order"] == "(40, 140, 50)"][0]
    axa.errorbar([2.0], [float(star["p_outbreak"])], yerr=err([star]), fmt="*", ms=8,
                 mfc="white", mec=C_B, ecolor=C_B, capsize=2, lw=0.9, ls="none",
                 zorder=5, label=r"$(40,140,50)$ at $N=10^6$")
    axa.set_xlabel(r"broadcast rate  $\lambda$")
    axa.set_ylabel("outbreak probability")
    axa.set_xticks([1.0, 2.0, 3.5])
    axa.set_xlim(0.72, 3.82)
    axa.set_ylim(-0.045, 1.02)
    axa.legend(fontsize=5.5, loc="upper left", handlelength=1.6, borderaxespad=0.1)
    panel_letter(axa, "a", dx=-0.165)
    axa.text(-0.105, 1.02, r"stance-memory campaigns ($N=10^5$ unless marked)",
             transform=axa.transAxes, fontsize=7.5, va="bottom", ha="left")
    axa.annotate("$0/50$ at both\norders at $\\lambda=1$", xy=(1.0, 0.0),
                 xytext=(1.08, 0.20), fontsize=6, color=GREY,
                 arrowprops=dict(arrowstyle="-", lw=0.6, color=GREY))
    z = [r for r in p1 if int(r["outbreaks"]) == 0][0]
    axa.text(0.985, 0.52,
             f"$0/50 \\Rightarrow$ Wilson $[0,\\,{float(z['ci_hi']):.4f}]$,\n"
             f"half-width ${float(z['half_width']):.4f}$ — exceeds\n"
             "the precision targets $0.03$ and $0.02$",
             transform=axa.transAxes, va="center", ha="right", fontsize=5.6,
             color="0.30")
    set_frame(axa)

    axb.errorbar(range(3), [float(r["p_outbreak"]) for r in p2], yerr=err(p2),
                 fmt="none", capsize=2, lw=1.0, ecolor=GREY, zorder=3)
    for i, (r, c) in enumerate(zip(p2, [C_A, C_B, C_C])):
        axb.plot([i], [float(r["p_outbreak"])], "o", ms=4.6, color=c, zorder=4)
        axb.text(i, max(float(r["ci_hi"]), 0.012) + 0.005,
                 f"$R={float(r['lam']) * float(r['q_T']) * math.log(1 / 0.95):.3f}$\n"
                 f"{int(r['outbreaks'])}/{int(r['replicates'])}",
                 ha="center", va="bottom", fontsize=6, color="0.25")
    axb.axhline(0.0, color=GREY, lw=0.5, ls=":")
    axb.set_xticks(range(3))
    axb.set_xticklabels([r["order"].replace(", ", ",") for r in p2], fontsize=6.5)
    axb.set_xlim(-0.55, 2.55)
    axb.set_ylim(-0.012, 0.145)
    axb.set_xlabel("campaign order")
    axb.set_ylabel("outbreak probability")
    panel_letter(axb, "b", dx=-0.21)
    axb.text(-0.15, 1.02, r"orientation-memory campaigns, $\lambda=26.5$, $N=10^5$",
             transform=axb.transAxes, fontsize=7.5, va="bottom", ha="left")
    set_frame(axb)
    fig.text(0.5, -0.055,
             "Intervals are NOMINAL fixed-sample Wilson 95% intervals. Replicate "
             "counts are adaptive (pilot of 50 extended from $\\hat p$, cap 1200, "
             "pilot pooled),\nso coverage under the realized design has not been "
             "assessed. Counts are printed per cell. The $N=10^6$ cells "
             "at $\\lambda=2$ (open stars) are\nOUTSIDE the adaptive rule: a fixed "
             "50-run design, not piloted and not extended, with no precision target.",
             ha="center", va="top", fontsize=5.6, color="0.35")
    fig.tight_layout()
    save(fig, outdir, "F2_outbreak_probability_by_order")
    plt.close(fig)


# ------------------------------------------------------------------ F3
def fig3(outdir):
    ag = read_table("F3_P6A_agent.csv")
    kn = read_table("F3_P6A_kinetic.csv")
    m = json.load(open(os.path.join(DATA, "F3_marks.json")))
    Af, tad = m["crossing_level"], m["adiabatic"]

    fig, ax = plt.subplots(figsize=(4.9, 3.5))
    ax.fill_between(ag["t"], ag["pct2p5_A"], ag["pct97p5_A"], color=C_A, alpha=0.18,
                    lw=0, zorder=2,
                    label="agent band: pointwise 2.5th-97.5th pct\n"
                          "ACROSS replicate trajectories (not a CI)")
    ax.plot(ag["t"], ag["mean_A"], color=C_A, lw=1.5, zorder=4,
            label=rf"agent mean  ($N=10^{{{int(math.log10(m['N']))}}}$, "
                  rf"{m['replicates']} replicates)")
    ax.plot(kn["t"], kn["A_kinetic"], color=C_B, lw=1.1, ls="--", zorder=5,
            label=rf"kinetic, finest grid $h={m['kinetic_h']:.4f}$")
    ax.axhline(Af, color=GREY, lw=0.8, ls=":", zorder=1)
    ax.text(1.0, Af + 0.012, rf"$A_f={Af}$", fontsize=6.5, color=GREY, va="bottom")
    ax.axvline(tad, color=C_C, lw=0.9, ls="-.", zorder=1)
    ax.text(tad - 1.5, 0.93, f"adiabatic\n$t_{{\\rm ad,f}}={tad:.3f}$", fontsize=6,
            color=C_C, ha="right", va="top")
    mu = m["agent_t_dagger_mean"]
    hlad = "/".join(f"{h:.7f}" for h in m["kinetic_h_ladder"])
    ax.plot([mu], [Af], marker="o", ms=4.5, mfc="white", mec=C_A, zorder=6)
    ax.annotate("$t^\\dagger$ at $A_f$:\n"
                f"agent mean {mu:.4f}, 95% CI "
                f"[{m['agent_t_dagger_mean_CI_lo']:.4f}, "
                f"{m['agent_t_dagger_mean_CI_hi']:.4f}]\n"
                f"   (Student-$t$, 49 df; half-width "
                f"{m['agent_t_dagger_mean_95_halfwidth']:.4f})\n"
                f"kinetic reference {m['kinetic_t_dagger_reference']:.4f} $\\pm$ "
                f"{m['kinetic_t_dagger_reference_unc']:.4f}\n"
                f"   (Richardson, $h$={hlad}, "
                f"$p$={m['kinetic_observed_order_in_h']:.3f})\n"
                f"kinetic finest grid {m['kinetic_t_dagger_finest_grid']:.4f} "
                "(curve shown)",
                xy=(mu, Af), xytext=(80.0, 1.00), fontsize=5.4, color="0.2",
                ha="left", va="top",
                arrowprops=dict(arrowstyle="-", lw=0.6, color="0.45"))
    ax.set_xlim(-2, 142)
    ax.set_ylim(-0.02, 1.02)
    ax.set_xlabel(r"time  $t$  (units of $\varepsilon^{-1}$)")
    ax.set_ylabel(r"active fraction  $A(t)$")
    ax.legend(fontsize=5.4, loc="lower left", handlelength=1.8, borderaxespad=0.3,
              labelspacing=0.5)
    set_frame(ax)
    fig.tight_layout()
    axi = fig.add_axes([0.625, 0.250, 0.255, 0.205])
    axi.fill_between(ag["t"], ag["pct2p5_A"], ag["pct97p5_A"], color=C_A, alpha=0.22,
                     lw=0)
    axi.plot(ag["t"], ag["mean_A"], color=C_A, lw=1.1)
    axi.plot(kn["t"], kn["A_kinetic"], color=C_B, lw=0.9, ls="--")
    axi.axhline(Af, color=GREY, lw=0.6, ls=":")
    axi.set_xlim(68.5, 72.0)
    axi.set_ylim(0.44, 0.70)
    axi.set_xticks([69, 70, 71, 72])
    axi.set_yticks([0.5, 0.6])
    axi.tick_params(labelsize=5.2, length=2, pad=1.2)
    set_frame(axi)
    save(fig, outdir, "F3_P6caseA_activity_trajectory")
    plt.close(fig)


# ------------------------------------------------------------------ F4
def fig4(outdir):
    onset = read_csv("F4a_class2_onset.csv")
    tr = read_table("F4b_P5_traces.csv")
    marks = {r["quantity"]: r for r in read_csv("F4_marks.csv")}
    lam_c = float(marks["lambda_c"]["value"])
    lam_fold = float(marks["lambda_fold"]["value"])
    lams = [float(r["lam"]) for r in onset]
    mf = [float(r["f_c_MF"]) for r in onset]
    mfe = [float(r["f_c_MF_unc"]) for r in onset]
    ag = [float(r["f50_agent"]) for r in onset]
    agl = [float(r["f50_agent"]) - float(r["f50_lo"]) for r in onset]
    agh = [float(r["f50_hi"]) - float(r["f50_agent"]) for r in onset]

    fig, (axa, axb) = plt.subplots(1, 2, figsize=(6.8, 3.1))
    axa.axvspan(lam_fold, lam_c, color="#f0f0f0", zorder=0)
    axa.errorbar(lams, mf, yerr=mfe, fmt="o", ms=5.0, color=C_A, capsize=2.5, lw=1.1,
                 ls="-", label=r"kinetic reference  $f_c^{\mathrm{MF}}$", zorder=4)
    axa.errorbar(lams, ag, yerr=[agl, agh], fmt="s", ms=4.4, mfc="white", mec=C_B,
                 ecolor=C_B, capsize=2.5, lw=1.1, ls="none",
                 label=r"agent $f_{50}$  ($N=5\times10^4$)", zorder=5)
    axa.axvline(lam_fold, color=C_C, lw=0.9, ls="--", zorder=1)
    axa.axvline(lam_c, color=C_D, lw=0.9, ls="-.", zorder=1)
    axa.set_yscale("log")
    axa.set_xlim(1.445, 1.995)
    axa.set_ylim(0.0045, 0.75)
    axa.text(lam_fold + 0.010, 0.62, rf"$\lambda_{{\rm fold}}={lam_fold:.6f}$",
             rotation=90, va="top", ha="left", fontsize=6, color=C_C)
    axa.text(lam_c - 0.010, 0.62, rf"$\lambda_c={lam_c:.5f}$", rotation=90, va="top",
             ha="right", fontsize=6, color=C_D)
    axa.text(1.72, 0.66, "bistable window", fontsize=6.5, color="0.35",
             ha="center")
    axa.set_xlabel(r"broadcast rate  $\lambda$")
    axa.set_ylabel(r"critical campaign reach  $f_c$")
    axa.legend(fontsize=6.2, loc="lower left", bbox_to_anchor=(0.10, 0.015),
               handlelength=1.8, borderaxespad=0.0)
    panel_letter(axa, "a")
    axa.text(-0.115, 1.02,
             r"backward onset: $\alpha=0.5$, $c_b=0.3$, $\varepsilon=1$, $r=1$",
             transform=axa.transAxes, fontsize=7.5, va="bottom", ha="left")
    set_frame(axa)

    sty = {"lam10_f001": (C_A, "-", r"$\lambda=1$, $f=0.01$"),
           "lam10_f01": ("#6a9fd0", "-", r"$\lambda=1$, $f=0.10$"),
           "lam20_f001": (C_B, "-", r"$\lambda=2$, $f=0.01$"),
           "lam20_f01": ("#d98b57", "--", r"$\lambda=2$, $f=0.10$")}
    axb.axvspan(20, 70, color="#f6f6f6", zorder=0)
    for key, (c, ls, lab) in sty.items():
        axb.fill_between(tr["t"], tr[key + "_lo"], tr[key + "_hi"], color=c,
                         alpha=0.16, lw=0, zorder=2)
        axb.plot(tr["t"], tr[key + "_mean"], color=c, ls=ls, lw=1.3, zorder=3,
                 label=lab)
    axb.axhline(0.5, color=GREY, lw=0.8, ls=":", zorder=1)
    axb.text(69.0, 0.515, r"$A^\ast=1/2$", ha="right", va="bottom", fontsize=6.5,
             color=GREY)
    axb.text(45, 0.33, "measurement window $[20,70]$", fontsize=6.5, color="0.35",
             ha="center")
    axb.annotate(r"extinction at $\lambda=1$", xy=(30.0, 0.0), xytext=(30.0, 0.12),
                 fontsize=6.5, color=C_A, ha="center",
                 arrowprops=dict(arrowstyle="-", lw=0.6, color=C_A))
    axb.text(0.985, 0.40, "bands: 2.5th-97.5th percentile\nacross 50 replicates",
             transform=axb.transAxes, ha="right", va="top", fontsize=5.6, color="0.30")
    axb.set_xlim(-1.5, 71)
    axb.set_ylim(-0.03, 0.70)
    axb.set_xlabel(r"time  $t$  (units of $\varepsilon^{-1}$)")
    axb.set_ylabel(r"active fraction  $A(t)$")
    axb.legend(fontsize=6.2, loc="upper left", handlelength=1.8, ncol=2,
               columnspacing=1.0)
    panel_letter(axb, "b")
    axb.text(-0.115, 1.02, r"$\alpha=2$, $c_b=0.5$, $r=1$, $N=10^5$",
             transform=axb.transAxes, fontsize=7.5, va="bottom", ha="left")
    set_frame(axb)
    fig.tight_layout()
    save(fig, outdir, "F4_onset_class2_and_class1")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--outdir", default=HERE, help="where to write the figures")
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    apply_style()
    for fn in (fig1, fig2, fig3, fig4):
        fn(a.outdir)


if __name__ == "__main__":
    main()
