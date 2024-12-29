import math
import matplotlib.pyplot as plt

def sieve_of_eratosthenes(limit):
    primes = [True] * (limit + 1)
    primes[0] = primes[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if primes[i]:
            for j in range(i * i, limit + 1, i):
                primes[j] = False
    return [i for i in range(2, limit + 1) if primes[i]]

def is_special_prime(p, q, primes):
    number = p**2 + 4*q**2
    return number in primes

def collect_special_primes(limit):
    primes = sieve_of_eratosthenes(limit)
    special_primes = []
    for p in primes:
        for q in primes:
            if p <= q:  # To avoid duplicates like (3,2) and (2,3)
                if is_special_prime(p, q, primes):
                    special_primes.append((p, q, p**2 + 4*q**2))
    return special_primes

# Set the limit for prime generation
limit = 10000

# Generate special primes
special_primes = collect_special_primes(limit)

# Separate data for visualization
p_values = [p for p, q, _ in special_primes]
q_values = [q for _, q, _ in special_primes]
special_prime_values = [prime for _, _, prime in special_primes]

# Visualization
plt.figure(figsize=(15, 5))

# Plot distribution of p and q
plt.subplot(1, 2, 1)
plt.scatter(p_values, q_values, alpha=0.5)
plt.xlabel('p')
plt.ylabel('q')
plt.title('Distribution of p and q for p^2 + 4q^2 primes')
plt.grid(True)

# Plot distribution of special primes against their index
plt.subplot(1, 2, 2)
plt.plot(range(len(special_prime_values)), special_prime_values, 'o', markersize=1)
plt.xlabel('Index of Special Prime')
plt.ylabel('Special Prime Number')
plt.title('Distribution of Special Primes')
plt.grid(True)

plt.tight_layout()
plt.show()

print(f"Number of special primes found: {len(special_primes)}")
