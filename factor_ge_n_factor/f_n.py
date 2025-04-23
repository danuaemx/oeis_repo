#!/usr/bin/env python3
"""
Compute for each N ≤ N_max the largest multiset A of factors of N
(such that product(A) = N and every a in A is ≥ |A|) and its size |A|.
"""

import sys
import math
from functools import lru_cache

def build_factors(n_max):
    """
    Precompute factors for every n in [1..n_max].
    We include 1 only when needed; here we exclude 1 since a ≥ |A| ≥ 1 always.
    """
    factors = {n: [] for n in range(1, n_max + 1)}
    for i in range(2, n_max + 1):
        for j in range(i, n_max + 1, i):
            factors[j].append(i)
    return factors

def find_multiset(n, k, factors):
    """
    Try to find a multiset of exactly k factors (all ≥ k) whose product is n.
    Returns a list of factors if found; otherwise None.
    """
    @lru_cache(None)
    def helper(remaining, depth):
        # If we've chosen k factors, check if we've used up the product
        if depth == k:
            return [] if remaining == 1 else None
        # Prune: if remaining < k ** (k - depth), impossible to reach product
        if remaining < k ** (k - depth):
            return None
        for a in factors.get(remaining, []):
            if a < k:
                continue
            # only proceed if dividing cleanly
            if remaining % a != 0:
                continue
            res = helper(remaining // a, depth + 1)
            if res is not None:
                return [a] + res
        return None

    return helper(n, 0)

def best_multiset_for(n, factors):
    """
    For a given n, find the maximum k and one corresponding multiset A.
    """
    # Maximum possible k is bounded by log2(n), but also by n >= k^k
    max_k = int(math.log(n, 2)) + 1 if n > 1 else 1
    best_k = 1
    best_A = [n]  # trivial multiset
    # Try from large k down to 1
    for k in range(max_k, 1, -1):
        if n < k ** k:
            continue
        A = find_multiset(n, k, factors)
        if A:
            best_k = k
            best_A = A
            break
    return best_k, sorted(best_A)

def main():
    N_max = 2048

    factors = build_factors(N_max)
    print(f"{'N':>6}  {'T(N)':>4}  A")
    print("-" * 40)
    for n in range(1, N_max + 1):
        k, A = best_multiset_for(n, factors)
        print(f"{n:6d}  {k:4d}  {A}")

if __name__ == "__main__":
    main()
