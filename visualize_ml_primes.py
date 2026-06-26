import os
import json
import numpy as np
import matplotlib.pyplot as plt
from openai import OpenAI
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
from sklearn.model_selection import cross_val_score, StratifiedKFold
from prime_utils import find_primes_of_form, load_prime_list, is_prime

XAI_API_KEY = os.getenv("XAI_API_KEY")
if XAI_API_KEY:
    client = OpenAI(api_key=XAI_API_KEY, base_url="https://api.x.ai/v1")
else:
    client = None

def analyze_with_grok(primes_found, p_range, q_range):
    if not client:
        return "No API key set"
    summaries = [{"p": p, "q": q, "v": v} for p, q, v in primes_found[:50]]
    messages = [
        {
            "role": "system",
            "content": "You are Grok, analyzing prime patterns in p^2 + 4q^2."
        },
        {
            "role": "user",
            "content": (
                f"Primes found in p∈[{p_range[0]},{p_range[-1]}], q∈[{q_range[0]},{q_range[-1]}]: "
                f"{len(primes_found)} total. Samples: {json.dumps(summaries)}. "
                "Analyze patterns."
            )
        }
    ]
    completion = client.chat.completions.create(
        model="grok-2-latest", messages=messages, temperature=0.1
    )
    return completion.choices[0].message.content

def engineer_features(p, q):
    return {
        "p": p, "q": q,
        "p_plus_q": p + q,
        "p_times_q": p * q,
        "p_mod_q": p % q if q else 0,
        "q_mod_p": q % p if p else 0,
        "p_minus_q": abs(p - q),
        "p_div_q": p / q if q else 0,
        "q_div_p": q / p if p else 0,
        "p_parity": p % 2,
        "q_parity": q % 2,
        "p_log": np.log(p) if p > 0 else 0,
        "q_log": np.log(q) if q > 0 else 0,
    }

def feature_vector(features):
    return [
        features["p"], features["q"],
        features["p_plus_q"], features["p_times_q"],
        features["p_mod_q"], features["q_mod_p"],
        features["p_minus_q"],
        features["p_div_q"], features["q_div_p"],
        features["p_parity"], features["q_parity"],
        features["p_log"], features["q_log"],
    ]

FEATURE_NAMES = [
    "p", "q", "p+q", "p*q", "p%q", "q%p",
    "|p-q|", "p/q", "q/p", "p%2", "q%2", "log(p)", "log(q)"
]

def build_dataset(prime_pairs, scale=3):
    X, y = [], []
    for p, q, _ in prime_pairs:
        X.append(feature_vector(engineer_features(p, q)))
        y.append(1)

    all_p = [p for p, q, _ in prime_pairs]
    all_q = [q for p, q, _ in prime_pairs]
    p_min, p_max = min(all_p), max(all_p)
    q_min, q_max = min(all_q), max(all_q)

    non_primes = []
    candidates = []
    for p in range(p_min, p_max + 1):
        for q in range(q_min, q_max + 1):
            candidates.append((p, q))

    np.random.shuffle(candidates)
    for p, q in candidates:
        if len(non_primes) >= len(prime_pairs) * scale:
            break
        if not is_prime(p * p + 4 * q * q):
            non_primes.append((p, q))

    for p, q in non_primes:
        X.append(feature_vector(engineer_features(p, q)))
        y.append(0)

    return np.array(X), np.array(y)

def train_and_evaluate(X, y):
    clf = RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(clf, X, y, cv=cv, scoring="accuracy")
    print(f"Cross-validation accuracy: {scores.mean():.4f} ± {scores.std():.4f}")

    clf.fit(X, y)
    return clf

def plot_feature_importance(clf):
    importances = clf.feature_importances_
    idx = np.argsort(importances)[::-1]
    plt.figure(figsize=(10, 6))
    plt.bar(range(len(importances)), importances[idx])
    plt.xticks(range(len(importances)), [FEATURE_NAMES[i] for i in idx], rotation=45, ha="right")
    plt.title("Random Forest Feature Importance")
    plt.tight_layout()
    plt.show()

def plot_primes_scatter(primes_list):
    p_vals = [p for p, q, _ in primes_list]
    q_vals = [q for _, q, _ in primes_list]
    vals = [v for _, _, v in primes_list]
    plt.figure(figsize=(10, 8))
    sc = plt.scatter(p_vals, q_vals, c=vals, cmap="viridis", alpha=0.6, s=20)
    plt.colorbar(sc, label="Prime Value")
    plt.xlabel("p"); plt.ylabel("q")
    plt.title("Distribution of Primes p² + 4q²")
    plt.show()

if __name__ == "__main__":
    prime_list = load_prime_list()
    print(f"Loaded {len(prime_list)} primes from dataset")

    rounds = int(input("Enter number of rounds (each expands range by 50): ") or "5")
    p_vals = [p for p in prime_list if p <= 50]
    q_vals = [q for q in prime_list if q <= 50]
    all_primes = []

    for r in range(rounds):
        found = find_primes_of_form(p_vals, q_vals)
        all_primes.extend(found)
        print(f"Round {r + 1}: p,q ≤ {p_vals[-1]}, found {len(found)} primes")
        if client:
            analysis = analyze_with_grok(found, p_vals, q_vals)
            print(f"  Grok: {analysis[:100]}...")
        p_vals = [p for p in prime_list if p <= 50 * (r + 2)]
        q_vals = [q for q in prime_list if q <= 50 * (r + 2)]

    all_primes = list(set(all_primes))
    print(f"\nTotal unique primes found: {len(all_primes)}")

    plot_primes_scatter(all_primes)

    print("\nBuilding ML dataset...")
    X, y = build_dataset(all_primes)
    print(f"Dataset: {X.shape[0]} samples, {X.shape[1]} features")
    print(f"Class balance: {y.sum()}/{len(y)} positive ({y.mean() * 100:.1f}%)")

    clf = train_and_evaluate(X, y)
    plot_feature_importance(clf)

    y_pred = clf.predict(X)
    print("\nClassification Report:")
    print(classification_report(y, y_pred, target_names=["Non-Prime", "Prime"]))

    cm = confusion_matrix(y, y_pred)
    ConfusionMatrixDisplay(cm, display_labels=["Non-Prime", "Prime"]).plot()
    plt.title("Confusion Matrix")
    plt.show()
