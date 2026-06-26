import numpy as np
import matplotlib.pyplot as plt
from prime_utils import load_prime_list

prime_list = load_prime_list()
primes = np.array(prime_list)
n = len(primes)
print(f"Dataset: {n} primes, from {primes[0]} to {primes[-1]}")

gaps = np.diff(primes)
print(f"Min gap: {gaps.min()}, Max gap: {gaps.max()}, Mean gap: {gaps.mean():.2f}")
print(f"Median gap: {np.median(gaps):.2f}, Std gap: {gaps.std():.2f}")

crammed = gaps == 2
print(f"Twin primes (gap=2): {crammed.sum()} pairs ({crammed.sum() / n * 100:.2f}%)")

max_gap_idx = np.argmax(gaps)
print(f"Largest gap: {gaps[max_gap_idx]} between {primes[max_gap_idx]} and {primes[max_gap_idx + 1]}")

fig, axes = plt.subplots(2, 3, figsize=(15, 10))

ax = axes[0, 0]
ax.plot(range(n), primes, linewidth=0.5, color="navy")
ax.set_xlabel("Index n"); ax.set_ylabel("nth Prime")
ax.set_title("Prime Growth (Thrilling)"); ax.grid(True, alpha=0.3)

ax = axes[0, 1]
ax.plot(range(1, n), gaps, linewidth=0.3, color="crimson", alpha=0.7)
ax.set_xlabel("Index n"); ax.set_ylabel("Gap to Next Prime")
ax.set_title("Prime Gaps"); ax.grid(True, alpha=0.3)

ax = axes[0, 2]
ax.hist(gaps, bins=100, color="steelblue", edgecolor="white", density=True)
ax.set_xlabel("Gap Size"); ax.set_ylabel("Density")
ax.set_title("Gap Distribution"); ax.set_xlim(0, 100)

ax = axes[1, 0]
density = np.arange(1, n + 1) / primes
ax.plot(range(n), density, linewidth=0.5, color="green")
ax.set_xlabel("Index n"); ax.set_ylabel("n / p_n")
ax.set_title("Prime Density (approaches 0)"); ax.grid(True, alpha=0.3)
ax.axhline(0, color="gray", linestyle="--", linewidth=0.5)

ax = axes[1, 1]
last_digit = primes % 10
for d in [1, 3, 7, 9]:
    count = (last_digit == d).sum()
    ax.bar(d, count, width=0.6, alpha=0.7)
ax.set_xlabel("Last Digit"); ax.set_ylabel("Count")
ax.set_title("Last Digit Distribution (mod 10)")
ax.set_xticks([1, 3, 7, 9])

ax = axes[1, 2]
mod3 = primes % 3
counts = [(mod3 == (n := i)).sum() for i in [1, 2]]
ax.bar(["1 mod 3", "2 mod 3"], counts, width=0.5, color="orange", alpha=0.7)
ax.set_title("Distribution mod 3")

plt.tight_layout()
plt.show()

print("\nTop 20 largest gaps:")
for i in np.argsort(gaps)[::-1][:20]:
    print(f"  {primes[i]} -> {primes[i+1]} (gap={gaps[i]})")

print(f"\nChebyshev bias (4n+3 vs 4n+1 up to {primes[-1]:,}):")
mod4 = primes % 4
print(f"  4n+1: {(mod4 == 1).sum()}, 4n+3: {(mod4 == 3).sum()}")
