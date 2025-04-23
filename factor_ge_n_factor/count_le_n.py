#!/usr/bin/env python3
"""
Compute all N ≤ N_max such that T(N) == T(N+1),
where T(N) is the maximum size of a multiset A of factors of N
with product(A)=N and every a∈A ≥ |A|.
"""

import sys
import math
from functools import lru_cache

def build_factors(n_max):
    """Precompute the list of factors ≥2 for each n in [1..n_max]."""
    factors = {n: [] for n in range(1, n_max + 1)}
    for i in range(2, n_max + 1):
        for j in range(i, n_max + 1, i):
            factors[j].append(i)
    return factors

def find_multiset(n, k, factors):
    """
    Try to find exactly k factors (all ≥ k) whose product is n.
    Returns one valid list of factors if possible, else None.
    """
    @lru_cache(None)
    def helper(remaining, depth):
        # If we've picked k factors, remaining must be 1
        if depth == k:
            return [] if remaining == 1 else None
        # Prune: smallest possible product of the rest is k^(k-depth)
        if remaining < k ** (k - depth):
            return None
        for a in factors.get(remaining, []):
            if a < k:
                continue
            if remaining % a != 0:
                continue
            rest = helper(remaining // a, depth + 1)
            if rest is not None:
                return [a] + rest
        return None

    return helper(n, 0)

def T_of(n, factors):
    """
    Return T(n), the maximum k for which there exists a multiset of k factors ≥ k whose product is n.
    """
    if n <= 1:
        return 1
    max_k = int(math.log(n, 2)) + 1
    for k in range(max_k, 1, -1):
        if n < k ** k:
            continue
        if find_multiset(n, k, factors):
            return k
    return 1

def main():
    N_max = 1000000

    # We need factors up to N_max+1 to compute T(N+1)
    factors = build_factors(N_max + 1)

    # Precompute T(n) for n = 1..N_max+1
    T = [0] * (N_max + 2)
    for n in range(1, N_max + 2):
        T[n] = T_of(n, factors)

    # Collect all N where T(N) == T(N+1)
    equal_consec = [n for n in range(1, N_max) if T[n] == T[n + 1]]

    print(f"Values of N ≤ {N_max} where T(N) = T(N+1):")
    print(equal_consec)
    print(f"Total: {len(equal_consec)}")
    print(f"Rat: {len(equal_consec)/N_max}")

if __name__ == "__main__":
    main()
