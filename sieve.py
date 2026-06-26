import matplotlib.pyplot as plt
from prime_utils import load_prime_list, load_prime_set, is_prime

def find_special_primes(prime_list):
    prime_set = load_prime_set()
    special = []
    for i, p in enumerate(prime_list):
        p2 = p * p
        for q in prime_list[:i + 1]:
            n = p2 + 4 * q * q
            if n in prime_set:
                special.append((p, q, n))
        if i % 100 == 0 and i > 0:
            print(f"Progress: checked {i}/{len(prime_list)} primes, found {len(special)} special primes")
    return special

if __name__ == "__main__":
    limit = int(input("Enter prime limit (e.g. 10000): ") or "10000")
    print(f"Loading primes up to {limit}...")
    all_primes = load_prime_list()
    primes = [p for p in all_primes if p <= limit]
    print(f"Using {len(primes)} primes up to {primes[-1] if primes else 0}")

    print("Searching for special primes of form p^2 + 4q^2...")
    special_primes = find_special_primes(primes)
    print(f"Found {len(special_primes)} special primes")

    if not special_primes:
        print("No special primes found.")
        exit()

    p_vals = [p for p, q, _ in special_primes]
    q_vals = [q for _, q, _ in special_primes]
    prime_vals = [v for _, _, v in special_primes]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    ax = axes[0, 0]
    scatter = ax.scatter(p_vals, q_vals, c=prime_vals, cmap="viridis", alpha=0.6, s=15)
    ax.set_xlabel("p"); ax.set_ylabel("q")
    ax.set_title("(p, q) Distribution of Special Primes")
    plt.colorbar(scatter, ax=ax, label="Prime Value")

    ax = axes[0, 1]
    ax.plot(range(len(prime_vals)), prime_vals, "o", markersize=2, color="tab:blue")
    ax.set_xlabel("Index"); ax.set_ylabel("Special Prime Value")
    ax.set_title("Special Primes by Discovery Order")
    ax.set_yscale("log")

    ax = axes[1, 0]
    gaps = [prime_vals[i + 1] - prime_vals[i] for i in range(len(prime_vals) - 1)]
    ax.hist(gaps, bins=50, color="tab:orange", edgecolor="white")
    ax.set_xlabel("Gap"); ax.set_ylabel("Frequency")
    ax.set_title("Gap Distribution Between Consecutive Special Primes")

    ax = axes[1, 1]
    ratios = [p / q for p, q in special_primes if q != 0]
    ax.hist(ratios, bins=40, color="tab:green", edgecolor="white")
    ax.set_xlabel("p/q Ratio"); ax.set_ylabel("Frequency")
    ax.set_title("Distribution of p/q Ratios")

    plt.tight_layout()
    plt.show()

    top10 = sorted(special_primes, key=lambda x: x[2], reverse=True)[:10]
    print("\nTop 10 largest special primes found:")
    for p, q, v in top10:
        print(f"  p={p}, q={q}, p^2+4q^2={v}")
