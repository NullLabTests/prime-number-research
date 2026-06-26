"""
Prime Number Research Analysis
===============================
Explores primes of the form R = p^2 + 4q^2 where p, q are primes.

Research questions:
  1) How does the density of R-primes decay as the search bound grows?
  2) What is the gap distribution — does it follow Cramer's Poisson model?
  3) Are p and q correlated?  What is the p/q ratio distribution?
  4) Which residue classes (mod 3, 4, 5, 8, 12) are over / under represented?
  5) Can a heuristic density law (power-law / log) be fitted?
  6) Do the R-primes obey Benford's first-digit law?
  7) How does an Ulam spiral of R-primes compare with all primes?
  8) Can a simple ML gap predictor beat the mean?

Output: PNG figures saved to ./figs/  + console summary.
"""

import os, json, math, itertools
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from scipy import stats as sp_stats
from collections import Counter

import prime_utils

# ---------- style ----------
plt.rcParams.update({
    "figure.dpi": 150,
    "font.size": 9,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
})

OUT = "figs"
os.makedirs(OUT, exist_ok=True)

# ---------- load data ----------
print("Loading primes…")
prime_list = prime_utils.load_prime_list()
prime_set  = prime_utils.load_prime_set()
print(f"  {len(prime_list)} primes loaded, largest = {prime_list[-1]:,}")

# ---------- 1. collect R-primes up to increasing bounds ----------
def collect_R_primes(prime_list, prime_set):
    """return list of (p, q, R) for R = p^2 + 4q^2, p,q prime, R in prime_set"""
    results = []
    max_R = max(prime_set)
    for i, p in enumerate(prime_list):
        p2 = p * p
        if p2 + 4 > max_R:
            break
        for q in prime_list[:i + 1]:
            R = p2 + 4 * q * q
            if R > max_R:
                break
            if R in prime_set:
                results.append((p, q, R))
        if (i + 1) % 500 == 0:
            print(f"  scanned p-index {i+1}/{len(prime_list)}, found {len(results)} R-primes")
    return results

print("\nCollecting R-primes (p^2 + 4q^2 ∈ primes) …")
R_primes = collect_R_primes(prime_list, prime_set)
print(f"  Found {len(R_primes)} R-primes in total")

R_primes.sort(key=lambda x: x[2])
p_vals  = np.array([x[0] for x in R_primes])
q_vals  = np.array([x[1] for x in R_primes])
R_vals  = np.array([x[2] for x in R_primes])
N       = len(R_vals)

# ====================================================================
#  FIGURE 1 —  Overview: discovery order, p/q ratios, gap histogram
# ====================================================================
print("\n[1/8] Overview figure …")
fig, axes = plt.subplots(2, 3, figsize=(16, 9))

ax = axes[0, 0]
sc = ax.scatter(p_vals, q_vals, c=np.log(R_vals), cmap="plasma", s=8, alpha=0.7)
ax.set_xlabel("p"); ax.set_ylabel("q")
ax.set_title("(p, q) Pairs that Yield R-Primes\n(colour = log R)")
plt.colorbar(sc, ax=ax, label="log R")

ax = axes[0, 1]
ax.plot(range(N), R_vals, linewidth=0.4, color="navy")
ax.set_xlabel("Discovery Index"); ax.set_ylabel("R")
ax.set_title(f"R-Primes in Discovery Order ({N} total)")
ax.set_yscale("log")

ax = axes[0, 2]
ratios = np.where(q_vals > 0, p_vals / q_vals.astype(float), np.nan)
ratios = ratios[~np.isnan(ratios)]
ax.hist(ratios, bins=80, color="teal", edgecolor="white", density=True)
ax.set_xlabel("p / q"); ax.set_ylabel("Density")
ax.set_title("Distribution of p / q Ratios")

ax = axes[1, 0]
gaps_R = np.diff(R_vals)
ax.hist(gaps_R, bins=80, color="crimson", edgecolor="white", density=True)
ax.set_xlabel("Gap to next R-prime"); ax.set_ylabel("Density")
ax.set_title("Gap Distribution of R-Primes")
ax.axvline(gaps_R.mean(), color="k", ls="--", label=f"mean={gaps_R.mean():.1f}")
ax.legend(fontsize=8)

ax = axes[1, 1]
# empirical CDF
sorted_gaps = np.sort(gaps_R)
ecdf = np.arange(1, len(sorted_gaps) + 1) / len(sorted_gaps)
ax.plot(sorted_gaps, ecdf, label="Empirical", color="crimson")
ax.plot(sorted_gaps, 1 - np.exp(-sorted_gaps / gaps_R.mean()),
        label="Exp(1/μ)", color="gray", ls="--")
ax.set_xlabel("Gap"); ax.set_ylabel("CDF")
ax.set_title("Gap CDF vs Exponential (Cramer model)")
ax.legend(fontsize=8)

ax = axes[1, 2]
ax.plot(p_vals, q_vals, "o", ms=1.5, alpha=0.3, color="purple")
z = np.polyfit(p_vals, q_vals, 1)
ax.plot(p_vals, np.polyval(z, p_vals), "r-", lw=1, label=f"slope={z[0]:.4f}")
ax.set_xlabel("p"); ax.set_ylabel("q")
ax.set_title("p vs q with Linear Fit")
ax.legend(fontsize=8)

plt.tight_layout()
fig.savefig(os.path.join(OUT, "01_overview.png"), bbox_inches="tight")
plt.close(fig)

# ====================================================================
#  FIGURE 2 —  Density decay  (cumulative count vs bound)
# ====================================================================
print("[2/8] Density analysis …")
bounds = np.logspace(2, np.log10(R_vals[-1]), 300).astype(int)
counts = np.searchsorted(R_vals, bounds)
total_primes_up_to_B = np.array([
    np.searchsorted(prime_list, b) for b in bounds
])
density = np.where(total_primes_up_to_B > 0,
                   counts / total_primes_up_to_B.astype(float), np.nan)

fig, axes = plt.subplots(1, 3, figsize=(16, 5))

ax = axes[0]
ax.plot(bounds, counts, color="darkgreen")
ax.set_xlabel("Bound B"); ax.set_ylabel("Cumulative R-Primes ≤ B")
ax.set_title("Growth of R-Primes with Bound")
ax.set_xscale("log"); ax.set_yscale("log")
# power-law fit
logB = np.log10(bounds[counts > 0])
logC = np.log10(counts[counts > 0])
slope, inter, *_ = sp_stats.linregress(logB, logC)
ax.plot(bounds[counts > 0], 10**(inter) * bounds[counts > 0]**slope,
        "r--", lw=1, label=f"power-law fit: slope={slope:.3f}")
ax.legend(fontsize=8)

ax = axes[1]
ax.plot(bounds, counts / bounds.astype(float), color="darkorange")
ax.set_xlabel("Bound B"); ax.set_ylabel("R-Primes / B")
ax.set_title("Raw Density (R-Primes per integer)")
ax.set_xscale("log"); ax.set_yscale("log")

ax = axes[2]
ax.plot(bounds, density, color="darkblue")
ax.set_xlabel("Bound B"); ax.set_ylabel("R-Primes / π(B)")
ax.set_title("Relative Density (R-Primes / All-Primes ≤ B)")
ax.set_xscale("log"); ax.set_yscale("log")
ax.grid(True, alpha=0.3)

plt.tight_layout()
fig.savefig(os.path.join(OUT, "02_density.png"), bbox_inches="tight")
plt.close(fig)

# ====================================================================
#  FIGURE 3 —  Modulo class analysis
# ====================================================================
print("[3/8] Modulo class analysis …")
moduli = [3, 4, 5, 6, 8, 12]
fig, axes = plt.subplots(2, 3, figsize=(16, 9))
for ax, m in zip(axes.flat, moduli):
    residues = R_vals % m
    counts_m = Counter(residues)
    classes = sorted(counts_m.keys())
    heights = [counts_m[c] for c in classes]
    ax.bar(classes, heights, width=0.6, color="steelblue", edgecolor="white")
    ax.set_xlabel(f"Residue mod {m}"); ax.set_ylabel("Count")
    ax.set_title(f"R-Primes mod {m}")
    ax.set_xticks(classes)
plt.tight_layout()
fig.savefig(os.path.join(OUT, "03_modulo_classes.png"), bbox_inches="tight")
plt.close(fig)

# ====================================================================
#  FIGURE 4 —  Chi-square test for uniformity
# ====================================================================
print("[4/8] Uniformity tests …")
fig, axes = plt.subplots(2, 3, figsize=(16, 9))
for ax, m in zip(axes.flat, moduli):
    residues = R_vals % m
    observed = [np.sum(residues == r) for r in range(m)]
    expected = [N / m] * m
    chi2, p_val = sp_stats.chisquare(observed)
    ax.bar(range(m), observed, color="steelblue", alpha=0.7, label="observed")
    ax.axhline(N / m, color="red", ls="--", label="expected (uniform)")
    ax.set_title(f"mod {m}  χ²={chi2:.1f}  p={p_val:.4f}")
    ax.set_xlabel("Residue"); ax.set_ylabel("Count")
    ax.legend(fontsize=7)
plt.tight_layout()
fig.savefig(os.path.join(OUT, "04_uniformity_tests.png"), bbox_inches="tight")
plt.close(fig)

# ====================================================================
#  FIGURE 5 —  Benford's first-digit law
# ====================================================================
print("[5/8] Benford analysis …")
def first_digit(x):
    return int(str(x)[0])

digits_R = np.array([first_digit(r) for r in R_vals])
benford_expected = np.array([np.log10(1 + 1 / d) for d in range(1, 10)])
observed_props = np.array([np.sum(digits_R == d) for d in range(1, 10)]) / N

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

ax = axes[0]
ax.bar(range(1, 10), observed_props, width=0.6, alpha=0.7, label="R-primes")
ax.plot(range(1, 10), benford_expected, "ro-", ms=5, label="Benford")
ax.set_xlabel("First Digit"); ax.set_ylabel("Proportion")
ax.set_title("Benford's Law — First Digit Distribution")
ax.legend(); ax.set_xticks(range(1, 10))

chi2_b, p_b = sp_stats.chisquare(observed_props * N, f_exp=benford_expected * N)
ax.text(0.5, 0.95, f"χ²={chi2_b:.1f}, p={p_b:.4f}",
        transform=ax.transAxes, ha="center", fontsize=9,
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

ax = axes[1]
# compare with ALL primes
digits_all = np.array([first_digit(p) for p in prime_list])
obs_all = np.array([np.sum(digits_all == d) for d in range(1, 10)]) / len(prime_list)
x = np.arange(1, 10)
ax.bar(x - 0.2, observed_props, 0.35, alpha=0.7, label="R-primes")
ax.bar(x + 0.2, obs_all, 0.35, alpha=0.7, label="All primes")
ax.plot(x, benford_expected, "ko-", ms=3, label="Benford")
ax.set_xlabel("First Digit"); ax.set_ylabel("Proportion")
ax.set_title("R-Primes vs All Primes — Benford Comparison")
ax.legend(fontsize=8); ax.set_xticks(range(1, 10))

plt.tight_layout()
fig.savefig(os.path.join(OUT, "05_benford.png"), bbox_inches="tight")
plt.close(fig)

# ====================================================================
#  FIGURE 6 —  Ulam spiral comparison
# ====================================================================
print("[6/8] Ulam spiral …")
def ulam_spiral(n_side):
    N = n_side * n_side
    x = y = 0
    dx, dy = 1, 0
    half = n_side // 2
    coords = {}
    for i in range(1, N + 1):
        coords[i] = (x, y)
        if abs(x) == abs(y) and (x > 0 or y == 0) or (x < 0 and y == -x):
            dx, dy = -dy, dx
        x += dx
        y += dy
    xs = [c[0] for c in coords.values()]
    ys = [c[1] for c in coords.values()]
    x_off = -min(xs)
    y_off = -min(ys)
    h = max(ys) - min(ys) + 1
    w = max(xs) - min(xs) + 1
    grid = np.zeros((h, w), dtype=bool)
    grid_R = np.zeros((h, w), dtype=bool)
    for i, (cx, cy) in coords.items():
        grid[cy + y_off, cx + x_off] = i in prime_set
        grid_R[cy + y_off, cx + x_off] = i in r_set
    return grid, grid_R

side = 201
r_set = set(R_vals)
grid, grid_R = ulam_spiral(side)

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

for ax, g, title, cmap in [
    (axes[0], grid, "All Primes (Ulam Spiral 201×201)", "Blues"),
    (axes[1], grid_R, "R-Primes Only (p²+4q²)", "Reds"),
    (axes[2], grid.astype(int) + grid_R.astype(int) * 2,
     "Overlay: blue=all primes  red=R-primes", None),
]:
    if cmap:
        ax.imshow(g, cmap=cmap, interpolation="none")
    else:
        # custom overlay
        rgb = np.zeros((*g.shape, 3))
        rgb[grid] = [0.6, 0.8, 1.0]      # light blue = all primes
        rgb[grid_R] = [1.0, 0.3, 0.3]    # red = R-primes
        rgb[grid & grid_R] = [1.0, 0.0, 1.0]  # magenta = overlap
        ax.imshow(rgb, interpolation="none")
    ax.set_title(title)
    ax.axis("off")

plt.tight_layout()
fig.savefig(os.path.join(OUT, "06_ulam_spiral.png"), bbox_inches="tight")
plt.close(fig)

# ====================================================================
#  FIGURE 7 —  ML gap predictor
# ====================================================================
print("[7/8] ML gap prediction …")
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score

if N >= 20:
    # predict gap to next R-prime from features of current (p,q,R)
    features, targets = [], []
    for i in range(N - 1):
        p, q, R = R_primes[i]
        p_next, q_next, R_next = R_primes[i + 1]
        gap = R_next - R
        features.append([
            p, q, R,
            p / (q + 1e-10),
            p % q if q else 0,
            q % p if p else 0,
            R % 3, R % 4, R % 5,
            np.log(R),
        ])
        targets.append(gap)
    X = np.array(features)
    y = np.array(targets)

    rf = RandomForestRegressor(n_estimators=150, max_depth=10, random_state=42, n_jobs=-1)
    scores = cross_val_score(rf, X, y, cv=5, scoring="neg_mean_absolute_error")
    mae_scores = -scores
    rf.fit(X, y)
    y_pred = rf.predict(X)

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    ax = axes[0]
    ax.plot(y, alpha=0.5, label="actual gap", color="gray")
    ax.plot(y_pred, alpha=0.7, label=f"RF predicted (CV MAE={mae_scores.mean():.1f}±{mae_scores.std():.1f})", color="crimson")
    ax.set_xlabel("Index"); ax.set_ylabel("Gap"); ax.set_title("Gap Prediction with Random Forest")
    ax.legend(fontsize=8)

    ax = axes[1]
    ax.scatter(y, y_pred, alpha=0.5, s=10)
    lims = [min(y.min(), y_pred.min()), max(y.max(), y_pred.max())]
    ax.plot(lims, lims, "r--", lw=1)
    ax.set_xlabel("Actual Gap"); ax.set_ylabel("Predicted Gap")
    ax.set_title("Predicted vs Actual"); ax.set_xscale("log"); ax.set_yscale("log")

    ax = axes[2]
    importances = rf.feature_importances_
    fnames = ["p", "q", "R", "p/q", "p%q", "q%p", "R%3", "R%4", "R%5", "log(R)"]
    idx = np.argsort(importances)[::-1]
    ax.bar(range(len(importances)), importances[idx], color="steelblue")
    ax.set_xticks(range(len(importances)))
    ax.set_xticklabels([fnames[i] for i in idx], rotation=45, ha="right", fontsize=8)
    ax.set_title("Feature Importance for Gap Prediction")

    plt.tight_layout()
    fig.savefig(os.path.join(OUT, "07_ml_gap_prediction.png"), bbox_inches="tight")
    plt.close(fig)

# ====================================================================
#  FIGURE 8 —  Correlation matrix & pairplots
# ====================================================================
print("[8/8] Correlation matrix …")
df_data = np.column_stack([p_vals, q_vals, R_vals, p_vals / (q_vals + 1e-10)])
labels = ["p", "q", "R", "p/q"]
corr = np.corrcoef(df_data.T)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

ax = axes[0]
im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
ax.set_xticks(range(4)); ax.set_yticks(range(4))
ax.set_xticklabels(labels); ax.set_yticklabels(labels)
for i in range(4):
    for j in range(4):
        ax.text(j, i, f"{corr[i, j]:.3f}", ha="center", va="center", fontsize=9,
                color="white" if abs(corr[i, j]) > 0.5 else "black")
ax.set_title("Pearson Correlation Matrix")
plt.colorbar(im, ax=ax)

ax = axes[1]
for idx, (i, j) in enumerate([(0, 1), (0, 2), (1, 2)]):
    ax = fig.add_subplot(1, 3, idx + 1)
    ax.scatter(df_data[:, i], df_data[:, j], s=3, alpha=0.3, color="steelblue")
    ax.set_xlabel(labels[i]); ax.set_ylabel(labels[j])
    ax.set_title(f"r = {corr[i, j]:.3f}")
    if idx == 2:
        axes[1].remove()

plt.tight_layout()
fig.savefig(os.path.join(OUT, "08_correlation.png"), bbox_inches="tight")
plt.close(fig)

# ====================================================================
#  Console summary
# ====================================================================
print("\n" + "=" * 60)
print("RESEARCH SUMMARY")
print("=" * 60)
print(f"Total R-primes found          : {N}")
print(f"Smallest R-prime              : {R_vals[0]:,}  (p={p_vals[0]}, q={q_vals[0]})")
print(f"Largest  R-prime              : {R_vals[-1]:,}  (p={p_vals[-1]}, q={q_vals[-1]})")
print(f"Mean gap                      : {gaps_R.mean():.2f}")
print(f"Median gap                    : {np.median(gaps_R):.2f}")
print(f"Max gap                       : {gaps_R.max()}")
print(f"p,q correlation               : {np.corrcoef(p_vals, q_vals)[0, 1]:.4f}")
print(f"p,R correlation               : {np.corrcoef(p_vals, R_vals)[0, 1]:.4f}")

# ratio statistics
ratio_mean = np.mean(ratios)
ratio_std  = np.std(ratios)
print(f"p/q ratio (mean ± std)        : {ratio_mean:.3f} ± {ratio_std:.3f}")

# density at largest bound
density_at_max = N / prime_list[-1] * 100
print(f"Density R/π(B) at B={prime_list[-1]:,}: {density_at_max:.4f}%")

# Modulo analysis highlight
for m in [4, 8]:
    residues = R_vals % m
    counts_m = Counter(residues)
    print(f"  mod {m} distribution: {dict(sorted(counts_m.items()))}")

# Benford
chi2_b, p_b = sp_stats.chisquare(observed_props * N, f_exp=benford_expected * N)
print(f"Benford χ²={chi2_b:.1f}, p={p_b:.4f}  (p<0.05 → significant deviation)")

if N >= 20:
    print(f"ML gap MAE (CV)               : {mae_scores.mean():.1f} ± {mae_scores.std():.1f}")
    mean_guess_mae = np.mean([abs(g - gaps_R.mean()) for g in gaps_R])
    print(f"Mean-guess MAE                : {mean_guess_mae:.1f}")

print(f"\nFigures saved to ./{OUT}/")
