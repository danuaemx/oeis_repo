import math
import sys

def sieve(n):
    """Return list of all primes ≤ n via a simple Sieve of Eratosthenes."""
    is_comp = [False] * (n + 1)
    primes = []
    for i in range(2, n + 1):
        if not is_comp[i]:
            primes.append(i)
            for j in range(i * i, n + 1, i):
                is_comp[j] = True
    return primes

def v_p_factorial(N, p):
    """Exponent of prime p in N! via repeated division."""
    e = 0
    while N:
        N //= p
        e += N
    return e

def M_of_N(N):
    """
    Compute M(N) = (ln ln N)^2 / N * sum_{2p ≤ N} [v_p(N!) mod ceil(log_p N)].
    """
    primes = sieve(N // 2)
    total_mod = 0
    lnN = math.log(N)
    for p in primes:
        if 2 * p > N:
            break
        vp = v_p_factorial(N, p)
        ceil_log_p = math.ceil(lnN / math.log(p))
        total_mod += vp % ceil_log_p
    return (math.log(math.log(N))**2) * total_mod / N

if __name__ == "__main__":
    N = 10**7+10**6
    print(f"M({N}) =", M_of_N(N))
