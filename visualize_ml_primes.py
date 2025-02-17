import os
import json
import matplotlib.pyplot as plt
from openai import OpenAI
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

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
        temperature=0.1,
    )
    
    return completion.choices[0].message.content, primes_found

def visualize_primes(primes):
    p_values = [p for p, q, _ in primes]
    q_values = [q for p, q, _ in primes]
    prime_values = [prime for _, _, prime in primes]
    
    plt.figure(figsize=(12, 8))
    plt.scatter(p_values, q_values, s=prime_values, c=prime_values, cmap='viridis', alpha=0.6)
    plt.colorbar(label='Prime Value')
    plt.xlabel('p')
    plt.ylabel('q')
    plt.title('Distribution of Primes p^2 + 4q^2')
    plt.show()

def machine_learning_predictor(primes):
    # Convert to binary classification problem: Is (p, q) a prime?
    X = [(p, q) for p, q, _ in primes]
    y = [1] * len(X)  # All are primes here
    
    # Add non-prime samples for balance
    non_primes = []
    for p in range(min(p for p, _, _ in primes), max(p for p, _, _ in primes) + 1):
        for q in range(min(q for _, q, _ in primes), max(q for _, q, _ in primes) + 1):
            if not primes_of_form(p, q):
                non_primes.append((p, q))
    non_primes = non_primes[:len(primes)]  # Balance the dataset
    X.extend(non_primes)
    y.extend([0] * len(non_primes))
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train Random Forest classifier
    clf = RandomForestClassifier(random_state=42)
    clf.fit(X_train, y_train)
    
    # Predict on test data
    y_pred = clf.predict(X_test)
    
    print("Machine Learning Accuracy:", accuracy_score(y_test, y_pred))
    
    return clf

if __name__ == "__main__":
    rounds = int(input("Enter number of rounds to iterate (each round increases p and q range by 10): "))
    
    p_start, p_end = 2, 10
    q_start, q_end = 1, 10
    all_primes = []

    for _ in range(rounds):
        analysis, primes = analyze_prime_distribution(p_start, p_end, q_start, q_end)
        print(f"Analysis for round {_ + 1}:")
        print(analysis)
        all_primes.extend(primes)
        p_start += 10
        p_end += 10
        q_start += 10
        q_end += 10

    visualize_primes(all_primes)

    # Machine Learning
    clf = machine_learning_predictor(all_primes)
    
    # Example prediction
    example_p, example_q = 20, 15
    prediction = clf.predict([(example_p, example_q)])[0]
    print(f"Prediction for p={example_p}, q={example_q}: {'Prime' if prediction else 'Not Prime'}")
