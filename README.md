# Prime Number Research

This repository explores the fascinating world of prime numbers, particularly those of the form \( p^2 + 4q^2 \). It's inspired by:

- The record-breaking Mersenne prime discovered by Luke Durant.
- Theoretical advancements in prime distribution by Green & Sawhney.

## Contents

### Scripts

- **primes.py**: Generates primes of the form \( p^2 + 4q^2 \) and uses the xAI API (Grok-2) to analyze patterns in their distribution.

- **sieve.py**: Implements the Sieve of Eratosthenes to generate primes up to a limit and finds special primes where both \( p \) and \( q \) are primes. Visualizes the distribution of these primes.

- **visualize_ml_primes.py**: Extends the functionality of `primes.py` by allowing iterative rounds of prime generation and analysis. Includes visualization of the primes found and a basic machine learning model (Random Forest Classifier) to predict prime numbers based on \( p \) and \( q \).

## Usage

- **primes.py**: ```python3 primes.py``` - This script runs a single analysis for a fixed range of \( p \) and \( q \).

- **sieve.py**: ```python3 sieve.py``` - Generates and visualizes special primes up to a set limit (currently 10,000).

- **visualize_ml_primes.py**: ```python3 visualize_ml_primes.py``` - Enter the number of rounds when prompted to extend the search for higher primes.

## Requirements

- Python 3.x
- Libraries: `openai`, `matplotlib`, `scikit-learn`
- xAI API Key (set as environment variable `XAI_API_KEY`)

## Setup

1. Clone the repository: ```git clone [your-repo-url]``` then ```cd prime-number-research```

2. Install dependencies: ```pip install openai matplotlib scikit-learn```

3. Set your xAI API key as an environment variable.

## Demo

Here is a demonstration image from running the script for 20 rounds:

<p align="center">
  <img src="https://i.imgur.com/sDV80WO.png" alt="Distribution of Primes p^2 + 4q^2 after 20 rounds" width="600">
</p>

The image shows the distribution of primes \( p^2 + 4q^2 \) with \( p \) on the x-axis and \( q \) on the y-axis. The color gradient represents the prime value, illustrating how the distribution evolves as we search for higher primes.

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests for review.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
