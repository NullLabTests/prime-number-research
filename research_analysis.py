#!/usr/bin/env python3
"""
Prime Research: Statistical Analysis of Primes of the Form p² + 4q²
(where p and q are also prime)

Exhaustive empirical investigation into primes expressible as p² + 4q²
with p, q prime. Generates 10 figures covering density, gaps, modular
biases, Benford's law, Ulam spiral, ML prediction, and correlation structure.

Research Questions:
1. What is the density relative to all primes? Power-law growth?
2. Gap distribution — does Cramer's exponential model hold?
3. Are p and q correlated? What is the p/q ratio distribution?
4. Which residue classes are over/under represented (mod 3,4,5,7,8,12)?
5. Do these primes follow Benford's first-digit law?
6. What does the Ulam spiral reveal about geometric structure?
7. Can ML predict gaps better than a mean-guess?
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import seaborn as sns
from scipy import stats
from sympy import isprime, primerange
import os, warnings, itertools
from collections import Counter, defaultdict
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score

warnings.filterwarnings('ignore')

# ---------- configuration ----------
SMALL_PRIME_LIMIT = 8_000
TOTAL_PRIMES_LIMIT = 1_000_000
OUT = "figs"
os.makedirs(OUT, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)
plt.rcParams['figure.dpi'] = 120
plt.rcParams['savefig.dpi'] = 150
np.random.seed(42)

# ---------- prime generation ----------
print("Generating primes...")
small_primes = list(primerange(2, SMALL_PRIME_LIMIT + 1))
print(f"  {len(small_primes):,} primes ≤ {SMALL_PRIME_LIMIT:,} for p,q candidates")

all_primes_1M = list(primerange(2, TOTAL_PRIMES_LIMIT + 1))
prime_set_large = set(all_primes_1M)
print(f"  {len(all_primes_1M):,} primes ≤ {TOTAL_PRIMES_LIMIT:,} for baseline")

# ---------- core search: r = p^2 + 4q^2 ----------
print("\nSearching for primes r = p² + 4q² (p,q prime)...")
special_triples = []
for i, p in enumerate(small_primes):
    p2 = p * p
    for q in small_primes:
        r = p2 + 4 * q * q
        if r > 2 and isprime(r):
            special_triples.append((p, q, r))
    if (i + 1) % 200 == 0:
        print(f"  scanned p-index {i+1}/{len(small_primes)}, found {len(special_triples)} triples")

special_triples.sort(key=lambda x: x[2])
p_vals = np.array([t[0] for t in special_triples])
q_vals = np.array([t[1] for t in special_triples])
r_vals = np.array([t[2] for t in special_triples])
N = len(r_vals)
print(f"  Total (p,q,r) triples: {N:,}")
print(f"  Range: {r_vals[0]:,} (p={p_vals[0]}, q={q_vals[0]}) → {r_vals[-1]:,}")

gaps = np.diff(r_vals)

# ====================================================================
#  FIGURE 1 — (p,q) scatter
# ====================================================================
print("\n[1/10] (p,q) scatter...")
fig, ax = plt.subplots(figsize=(10, 8))
sc = ax.scatter(p_vals, q_vals, c=np.log10(r_vals), cmap='viridis',
                alpha=0.7, s=15, edgecolors='none')
cbar = plt.colorbar(sc, ax=ax)
cbar.set_label(r'$\log_{10} r$', fontsize=11)
ax.set_xlabel('p (prime)'); ax.set_ylabel('q (prime)')
ax.set_title(r'Prime Pairs (p,q) Yielding Prime $r = p^2 + 4q^2$', fontsize=13)
ax.set_aspect('equal', adjustable='box')
ax.grid(True, alpha=0.3)
plt.tight_layout()
fig.savefig(f'{OUT}/01_pq_scatter.png', bbox_inches='tight')
plt.close()

# ====================================================================
#  FIGURE 2 — Gap distribution + Q-Q plot
# ====================================================================
print("[2/10] Gap distribution...")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

ax = axes[0]
sns.histplot(gaps, bins=60, kde=True, color='steelblue', ax=ax, stat='density')
mu = gaps.mean()
ax.plot(np.linspace(0, np.percentile(gaps, 99), 200),
        (1/mu) * np.exp(-np.linspace(0, np.percentile(gaps, 99), 200)/mu),
        'r--', lw=2, label=f'Exp(1/{mu:.0f})')
ax.set_xlabel('Gap to next r-prime'); ax.set_ylabel('Density')
ax.set_title('Gap Distribution with Exponential Fit'); ax.legend()
ax.set_xlim(0, np.percentile(gaps, 99.5))

ax = axes[1]
stats.probplot(gaps, dist=stats.expon, plot=ax)
ax.set_title('Q-Q Plot vs Exponential')
ax.grid(True, alpha=0.3)
plt.tight_layout()
fig.savefig(f'{OUT}/02_gap_distribution.png', bbox_inches='tight')
plt.close()

# ====================================================================
#  FIGURE 3 — Density / cumulative count
# ====================================================================
print("[3/10] Density analysis...")
bins = np.logspace(3, np.log10(r_vals[-1]), 30)
special_counts, _ = np.histogram(r_vals, bins)
total_counts = np.array([sum(1 for pr in all_primes_1M if lo <= pr < hi)
                         for lo, hi in zip(bins[:-1], bins[1:])])
bin_centers = np.sqrt(bins[:-1] * bins[1:])
special_cum = np.cumsum(special_counts)
total_cum = np.cumsum(total_counts)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

ax = axes[0]
ax.plot(bin_centers, special_cum, 'o-', color='darkorange', lw=2, ms=5,
        label=f'r-primes (N={N:,})')
ax.plot(bin_centers, total_cum / 50, 's--', color='steelblue', lw=1.5, ms=4,
        label='All primes /50')
mask = (bin_centers > 1000) & (special_cum > 0)
slope, inter = np.polyfit(np.log10(bin_centers[mask]), np.log10(special_cum[mask]), 1)
ax.plot(bin_centers[mask], 10**inter * bin_centers[mask]**slope, 'k--', lw=1,
        label=f'power-law fit (α={slope:.3f})')
ax.set_xscale('log'); ax.set_yscale('log')
ax.set_xlabel('Bound B'); ax.set_ylabel('Cumulative count ≤ B')
ax.set_title('Cumulative Count: r-Primes vs All Primes')
ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

ax = axes[1]
density = np.where(total_cum > 0, special_cum / total_cum * 100, np.nan)
ax.plot(bin_centers, density, '-', color='darkgreen')
ax.set_xscale('log')
ax.set_xlabel('Bound B'); ax.set_ylabel('Relative density (%)')
ax.set_title('r-Primes as % of All Primes ≤ B')
ax.grid(True, alpha=0.3)
plt.tight_layout()
fig.savefig(f'{OUT}/03_density_cumulative.png', bbox_inches='tight')
plt.close()

# ====================================================================
#  FIGURE 4 — p/q ratio
# ====================================================================
print("[4/10] p/q ratio...")
fig, ax = plt.subplots(figsize=(9, 5))
ratios = p_vals / q_vals.astype(float)
sns.histplot(ratios, bins=40, kde=True, color='teal', ax=ax, stat='density')
ax.axvline(np.median(ratios), color='red', ls='--', lw=2, label=f'Median={np.median(ratios):.3f}')
ax.axvline(1.0, color='gray', ls=':', lw=1.5, label='p=q')
ax.set_xlabel(r'$p/q$'); ax.set_ylabel('Density')
ax.set_title('Distribution of p/q Ratios'); ax.legend()
plt.tight_layout()
fig.savefig(f'{OUT}/04_pq_ratio.png', bbox_inches='tight')
plt.close()

# ====================================================================
#  FIGURE 5 — Residue class biases
# ====================================================================
print("[5/10] Residue class analysis...")
moduli = [3, 4, 5, 7, 8, 12]
fig, axes = plt.subplots(2, 3, figsize=(15, 9))
axes = axes.flatten()

for idx, m in enumerate(moduli):
    ax = axes[idx]
    residues = r_vals % m
    counts = Counter(residues)
    classes = sorted(counts.keys())
    freqs = [counts[c] / N for c in classes]
    colors = ['#e74c3c' if f > 2.0/m else '#3498db' for f in freqs]
    ax.bar(classes, freqs, color=colors, edgecolor='black', linewidth=0.5)
    ax.axhline(1.0/m, color='green', ls='--', lw=2, label=f'Uniform ({1/m:.3f})')
    ax.set_xlabel(f'Residue mod {m}'); ax.set_ylabel('Frequency')
    ax.set_title(f'Mod {m} Distribution'); ax.set_xticks(classes)
    ax.legend(fontsize=8); ax.grid(True, axis='y', alpha=0.3)

plt.suptitle('Residue Class Distribution of r-Primes\n(Red = over-represented vs uniform)', fontsize=14)
plt.tight_layout()
fig.savefig(f'{OUT}/05_residue_classes.png', bbox_inches='tight')
plt.close()

# ====================================================================
#  FIGURE 6 — Benford's law
# ====================================================================
print("[6/10] Benford analysis...")
def first_digit(x): return int(str(x)[0])

digits = np.array([first_digit(r) for r in r_vals])
benford_exp = np.array([np.log10(1 + 1/d) for d in range(1, 10)])
obs = np.array([np.sum(digits == d) / N for d in range(1, 10)])

# all primes comparison
all_digits = np.array([first_digit(p) for p in all_primes_1M])
obs_all = np.array([np.sum(all_digits == d) / len(all_primes_1M) for d in range(1, 10)])

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

ax = axes[0]
x = np.arange(1, 10)
ax.bar(x - 0.2, obs, 0.35, alpha=0.85, label='r-primes', color='#9b59b6')
ax.bar(x + 0.2, benford_exp, 0.35, alpha=0.85, label='Benford', color='#f39c12')
ax.set_xlabel('First Digit'); ax.set_ylabel('Proportion')
ax.set_title(f"Benford's Law — r-Primes (N={N:,})")
ax.set_xticks(x); ax.legend(); ax.grid(True, axis='y', alpha=0.3)

ax = axes[1]
ax.bar(x - 0.2, obs, 0.35, alpha=0.85, label='r-primes', color='#9b59b6')
ax.bar(x + 0.2, obs_all, 0.35, alpha=0.85, label='All primes', color='#2ecc71')
ax.plot(x, benford_exp, 'ko-', ms=4, label='Benford theory')
ax.set_xlabel('First Digit'); ax.set_ylabel('Proportion')
ax.set_title('r-Primes vs All Primes — Benford Comparison')
ax.set_xticks(x); ax.legend(fontsize=8); ax.grid(True, axis='y', alpha=0.3)

chi2_r, p_r = stats.chisquare(obs * N, f_exp=benford_exp * N)
ax.text(0.5, 0.95, f'r-primes χ²={chi2_r:.1f}, p={p_r:.2e}',
        transform=ax.transAxes, ha='center', fontsize=9,
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
fig.savefig(f'{OUT}/06_benford.png', bbox_inches='tight')
plt.close()

# ====================================================================
#  FIGURE 7 — Gap vs size trend
# ====================================================================
print("[7/10] Gap vs size trend...")
fig, ax = plt.subplots(figsize=(10, 5))
mid = (r_vals[:-1] + r_vals[1:]) / 2
ax.scatter(mid, gaps, alpha=0.3, s=8, color='darkred')
window = max(5, len(gaps) // 50)
if window < len(gaps):
    ma = np.convolve(gaps, np.ones(window)/window, mode='valid')
    ma_x = mid[window//2 : window//2 + len(ma)]
    ax.plot(ma_x, ma, 'k-', lw=2, label=f'Moving avg (w={window})')
ax.set_xlabel('r value (midpoint)'); ax.set_ylabel('Gap to next r-prime')
ax.set_title('Gap Size vs Prime Magnitude')
ax.set_xscale('log'); ax.set_yscale('log')
ax.legend(); ax.grid(True, alpha=0.3)
plt.tight_layout()
fig.savefig(f'{OUT}/07_gap_vs_size.png', bbox_inches='tight')
plt.close()

# ====================================================================
#  FIGURE 8 — Ulam spiral
# ====================================================================
print("[8/10] Ulam spiral...")
def build_ulam_spiral(n_side, prime_set, r_set):
    N = n_side * n_side
    x = y = 0; dx, dy = 1, 0
    coords = {}
    step = 1
    steps_in_leg = 0
    leg = 0
    for i in range(1, N + 1):
        coords[i] = (x, y)
        x += dx; y += dy
        steps_in_leg += 1
        if steps_in_leg == step:
            steps_in_leg = 0
            leg += 1
            dx, dy = -dy, dx
            if leg % 2 == 0:
                step += 1
    xs = [c[0] for c in coords.values()]
    ys = [c[1] for c in coords.values()]
    x_off, y_off = -min(xs), -min(ys)
    h, w = max(ys) - min(ys) + 1, max(xs) - min(xs) + 1
    grid_all = np.zeros((h, w), dtype=bool)
    grid_r = np.zeros((h, w), dtype=bool)
    for i, (cx, cy) in coords.items():
        grid_all[cy + y_off, cx + x_off] = i in prime_set
        grid_r[cy + y_off, cx + x_off] = i in r_set
    return grid_all, grid_r

side = 301
r_set = set(r_vals)
prime_set_m = set(all_primes_1M[:100000])
grid_all, grid_r = build_ulam_spiral(side, prime_set_m, r_set)

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

for ax, g, title in [
    (axes[0], grid_all, 'All Primes (Ulam Spiral)'),
    (axes[1], grid_r, 'r-Primes Only (p²+4q²)'),
    (axes[2], None, 'Overlay: blue=all  red=r-primes  magenta=both'),
]:
    if g is not None:
        ax.imshow(g, cmap='Blues', interpolation='none')
    else:
        rgb = np.zeros((*grid_all.shape, 3))
        rgb[grid_all] = [0.6, 0.8, 1.0]
        rgb[grid_r] = [1.0, 0.3, 0.3]
        rgb[grid_all & grid_r] = [1.0, 0.0, 1.0]
        ax.imshow(rgb, interpolation='none')
    ax.set_title(title); ax.axis('off')

plt.tight_layout()
fig.savefig(f'{OUT}/08_ulam_spiral.png', bbox_inches='tight')
plt.close()

# ====================================================================
#  FIGURE 9 — ML gap prediction
# ====================================================================
print("[9/10] ML gap prediction...")
if N >= 50:
    features, targets = [], []
    for i in range(N - 1):
        p, q, R = special_triples[i]
        _, _, R_next = special_triples[i + 1]
        gap = R_next - R
        features.append([
            p, q, R, p / (q + 1e-10),
            p % q if q else 0, q % p if p else 0,
            R % 3, R % 4, R % 5, R % 7, R % 8,
            np.log(R)
        ])
        targets.append(gap)
    X = np.array(features); y = np.array(targets)

    rf = RandomForestRegressor(n_estimators=150, max_depth=10, random_state=42, n_jobs=-1)
    scores = cross_val_score(rf, X, y, cv=5, scoring='neg_mean_absolute_error')
    mae_scores = -scores
    rf.fit(X, y)
    y_pred = rf.predict(X)
    mean_guess_mae = np.mean(np.abs(y - y.mean()))

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    ax = axes[0]
    ax.plot(y, alpha=0.4, label='actual', color='gray')
    ax.plot(y_pred, alpha=0.7, label=f'RF pred (CV MAE={mae_scores.mean():.0f}±{mae_scores.std():.0f})', color='crimson')
    ax.axhline(y.mean(), color='blue', ls='--', lw=1, label=f'mean ({y.mean():.0f})')
    ax.set_xlabel('Index'); ax.set_ylabel('Gap'); ax.set_title('Gap Prediction — Random Forest')
    ax.legend(fontsize=8)

    ax = axes[1]
    ax.scatter(y, y_pred, alpha=0.4, s=10)
    lims = [min(y.min(), y_pred.min()), max(y.max(), y_pred.max())]
    ax.plot(lims, lims, 'r--', lw=1)
    ax.set_xlabel('Actual'); ax.set_ylabel('Predicted')
    ax.set_title(f'Predicted vs Actual  (mean MAE={mean_guess_mae:.0f})')

    ax = axes[2]
    fnames = ['p','q','R','p/q','p%q','q%p','R%3','R%4','R%5','R%7','R%8','log(R)']
    imp = rf.feature_importances_
    idx = np.argsort(imp)[::-1]
    ax.bar(range(len(imp)), imp[idx], color='steelblue')
    ax.set_xticks(range(len(imp)))
    ax.set_xticklabels([fnames[i] for i in idx], rotation=45, ha='right', fontsize=8)
    ax.set_title('Feature Importance')

    plt.tight_layout()
    fig.savefig(f'{OUT}/09_ml_gap_prediction.png', bbox_inches='tight')
    plt.close()

# ====================================================================
#  FIGURE 10 — Correlation matrix
# ====================================================================
print("[10/10] Correlation matrix...")
df = np.column_stack([p_vals, q_vals, r_vals, p_vals / (q_vals + 1e-10)])
labels = ['p', 'q', 'R', 'p/q']
corr = np.corrcoef(df.T)

fig = plt.figure(figsize=(14, 5))
gs = fig.add_gridspec(1, 4, width_ratios=[1, 1, 1, 1], wspace=0.35)

ax_heat = fig.add_subplot(gs[0])
im = ax_heat.imshow(corr, cmap='RdBu_r', vmin=-1, vmax=1)
ax_heat.set_xticks(range(4)); ax_heat.set_yticks(range(4))
ax_heat.set_xticklabels(labels); ax_heat.set_yticklabels(labels)
for i in range(4):
    for j in range(4):
        ax_heat.text(j, i, f'{corr[i,j]:.3f}', ha='center', va='center', fontsize=9,
                color='white' if abs(corr[i,j]) > 0.5 else 'black')
ax_heat.set_title('Correlation Matrix')
plt.colorbar(im, ax=ax_heat)

for idx, (i, j) in enumerate([(0, 1), (0, 2), (1, 2)]):
    ax = fig.add_subplot(gs[idx + 1])
    ax.scatter(df[:, i], df[:, j], s=2, alpha=0.2, color='steelblue')
    ax.set_xlabel(labels[i]); ax.set_ylabel(labels[j])
    ax.set_title(f'ρ = {corr[i,j]:.3f}')

plt.tight_layout()
fig.savefig(f'{OUT}/10_correlation.png', bbox_inches='tight')
plt.close()

# ====================================================================
#  SUMMARY
# ====================================================================
print("\n" + "="*70)
print("RESEARCH SUMMARY")
print("="*70)
print(f"Total r-primes found          : {N:,}")
print(f"Search bound p,q ≤            : {SMALL_PRIME_LIMIT:,}")
print(f"Smallest r                    : {r_vals[0]:,}  (p={p_vals[0]}, q={q_vals[0]})")
print(f"Largest  r                    : {r_vals[-1]:,}  (p={p_vals[-1]}, q={q_vals[-1]})")
print(f"Mean gap                      : {gaps.mean():.1f}")
print(f"Median gap                    : {np.median(gaps):.1f}")
print(f"Max gap                       : {gaps.max():,}")
print(f"p,q Pearson ρ                 : {np.corrcoef(p_vals, q_vals)[0,1]:.4f}")
print(f"Density at max bound          : {N / all_primes_1M[-1] * 100:.4f}%")
print(f"Power-law exponent α          : {slope:.3f}")

print("\nResidue class biases (% in most frequent class):")
for m in moduli:
    residues = r_vals % m
    c = Counter(residues)
    best = c.most_common(1)[0]
    print(f"  mod {m:2d}: most={best[0]}  ({best[1]/N*100:.1f}%)  uniform={100/m:.1f}%")

chi2_r, p_r = stats.chisquare(obs * N, f_exp=benford_exp * N)
print(f"Benford χ²={chi2_r:.1f}, p={p_r:.2e}")
if N >= 50:
    print(f"ML gap MAE (CV)               : {mae_scores.mean():.0f} ± {mae_scores.std():.0f}")
    print(f"Mean-guess MAE                : {mean_guess_mae:.0f}")
print(f"\nAll figures saved to ./{OUT}/")
