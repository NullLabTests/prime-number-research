import os
import json
from openai import OpenAI
from prime_utils import find_primes_of_form, load_prime_set, load_prime_list

XAI_API_KEY = os.getenv("XAI_API_KEY")
if not XAI_API_KEY:
    raise ValueError("xAI API key not found. Set XAI_API_KEY environment variable.")

client = OpenAI(api_key=XAI_API_KEY, base_url="https://api.x.ai/v1")

def analyze_with_grok(primes_found, p_range, q_range):
    summaries = []
    for p, q, prime in primes_found[:50]:
        summaries.append({"p": p, "q": q, "p^2+4q^2": prime})
    total = len(primes_found)

    messages = [
        {
            "role": "system",
            "content": "You are Grok, a highly analytical AI exploring mathematical patterns in prime numbers of the form p^2 + 4q^2."
        },
        {
            "role": "user",
            "content": (
                f"Analyze these primes of the form p^2 + 4q^2 where p in [{p_range[0]},{p_range[-1]}], "
                f"q in [{q_range[0]},{q_range[-1]}]. Found {total} primes. "
                f"Sample (first {min(50, total)}): {json.dumps(summaries)}. "
                "Look for patterns in distribution, density as p/q grow, parity, "
                "or any interesting mathematical observations."
            )
        }
    ]

    completion = client.chat.completions.create(
        model="grok-2-latest",
        messages=messages,
        temperature=0.1,
    )
    return completion.choices[0].message.content

if __name__ == "__main__":
    prime_list = load_prime_list()
    print(f"Loaded {len(prime_list)} primes from dataset (up to {prime_list[-1]})")

    p_vals = [p for p in prime_list if p <= 200]
    q_vals = [q for q in prime_list if q <= 200]
    primes_found = find_primes_of_form(p_vals, q_vals)
    print(f"Found {len(primes_found)} primes of form p^2 + 4q^2 (p,q up to 200)")
    print(f"Largest: {max(primes_found, key=lambda x: x[2])}")

    if primes_found and XAI_API_KEY:
        analysis = analyze_with_grok(primes_found, p_vals, q_vals)
        print("\nGrok Analysis:")
        print(analysis)
