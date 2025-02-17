import os
from openai import OpenAI
import json

# Ensure you have your xAI API key set as an environment variable
XAI_API_KEY = os.getenv("XAI_API_KEY")

if not XAI_API_KEY:
    raise ValueError("xAI API key not found. Please set the XAI_API_KEY environment variable.")

client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1",
)

def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def primes_of_form(p, q):
    number = p**2 + 4*q**2
    return is_prime(number)

def analyze_prime_distribution(p_start, p_end, q_start, q_end):
    primes_found = []
    for p in range(p_start, p_end + 1):
        for q in range(q_start, q_end + 1):
            if primes_of_form(p, q):
                primes_found.append((p, q, p**2 + 4*q**2))
    
    # Here we use Grok to analyze or predict patterns in prime distribution
    messages = [
        {
            "role": "system",
            "content": "You are Grok, a highly analytical AI designed to explore mathematical patterns."
        },
        {
            "role": "user",
            "content": f"Analyze these primes of the form p^2 + 4q^2 where ({p_start}<=p<={p_end} and {q_start}<=q<={q_end}): {json.dumps(primes_found)}. Look for any patterns in distribution, frequency, or any interesting observations."
        }
    ]
    
    completion = client.chat.completions.create(
        model="grok-2-latest",
        messages=messages,
        temperature=0.1,  # Lower temperature for more deterministic responses
    )
    
    return completion.choices[0].message.content, primes_found

if __name__ == "__main__":
    analysis, primes = analyze_prime_distribution(2, 10, 1, 10)
    print("Analysis from Grok:")
    print(analysis)
    print("\nPrimes found:")
    for p, q, prime in primes:
        print(f"p={p}, q={q}, prime={prime}")
