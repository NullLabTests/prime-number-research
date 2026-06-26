# Prime Number Research

Exploring prime numbers, especially those of the form \( p^2 + 4q^2 \) where both \( p \) and \( q \) are primes.

## Contents

### Shared Utilities
- **prime_utils.py** — Common prime operations: optimized `is_prime()`, Sieve of Eratosthenes, `find_primes_of_form()`, and a loader for the bundled 100,000 prime dataset (`log_100000.txt`). Used by all scripts below.

### Scripts
- **primes.py** — Finds primes of the form \( p^2 + 4q^2 \) using the 100K dataset, then sends results to xAI's Grok API for pattern analysis.

- **sieve.py** — Searches for special primes up to a user-specified limit, with multi-panel visualizations (distribution, gaps, p/q ratios).

- **visualize_ml_primes.py** — Iterative search with expanding ranges. Trains a Random Forest classifier with engineered features (p mod q, p/q ratios, parity, etc.) to distinguish prime vs non-prime \( p^2 + 4q^2 \) values. Includes cross-validation, feature importance, and confusion matrix.

- **analyze_dataset.py** — Exploratory analysis of the bundled 100,000 prime dataset: gap distribution, twin primes, Chebyshev bias, last-digit frequency, and density plots.

### Data
- **log_100000.txt** — First 100,000 prime numbers (PHP serialized array, up to 1,299,709).
- **100000_primes.zip** — Same data compressed.

## Requirements

- Python 3.x
- `pip install matplotlib scikit-learn openai numpy`
- xAI API key (set `XAI_API_KEY`) — required only for `primes.py` Grok analysis

## Usage

```bash
# Explore the 100K prime dataset
python3 analyze_dataset.py

# Find special primes p^2 + 4q^2 with visualizations
python3 sieve.py

# ML-based analysis with iterative range expansion
python3 visualize_ml_primes.py

# Grok-powered pattern analysis (requires XAI_API_KEY)
python3 primes.py
```

## License

MIT
