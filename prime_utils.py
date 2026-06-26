import re
import math
import functools

PRIME_DATASET_PATH = "log_100000.txt"

@functools.lru_cache(maxsize=1)
def load_prime_dataset():
    primes = {}
    with open(PRIME_DATASET_PATH) as f:
        content = f.read()
    for m in re.finditer(r'(\d+)\s*=>\s*(\d+)', content):
        idx, prime = int(m.group(1)), int(m.group(2))
        primes[idx] = prime
    return primes

@functools.lru_cache(maxsize=1)
def load_prime_set():
    return set(load_prime_dataset().values())

@functools.lru_cache(maxsize=1)
def load_prime_list():
    d = load_prime_dataset()
    return [d[i] for i in range(len(d))]

def sieve_of_eratosthenes(limit):
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit ** 0.5) + 1):
        if sieve[i]:
            step = i
            start = i * i
            sieve[start:limit + 1:step] = [False] * ((limit - start) // step + 1)
    return [i for i in range(2, limit + 1) if sieve[i]]

def is_prime(n):
    if n < 2:
        return False
    try:
        prime_set = load_prime_set()
        if n <= max(prime_set):
            return n in prime_set
    except (FileNotFoundError, ValueError):
        pass
    if n % 2 == 0:
        return n == 2
    limit = int(math.isqrt(n))
    for i in range(3, limit + 1, 2):
        if n % i == 0:
            return False
    return True

def primes_of_form(p, q):
    return is_prime(p * p + 4 * q * q)

def find_primes_of_form(p_range, q_range):
    results = []
    for p in p_range:
        p2 = p * p
        for q in q_range:
            n = p2 + 4 * q * q
            if is_prime(n):
                results.append((p, q, n))
    return results
