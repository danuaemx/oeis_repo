import math
import sys

def sieve(n):
    """Return list of all primes ≤ n via simple sieve."""
    is_comp = [False]*(n+1)
    primes = []
    for i in range(2, n+1):
        if not is_comp[i]:
            primes.append(i)
            for j in range(i*i, n+1, i):
                is_comp[j] = True
    return primes

def v_p_factorial(N, p):
    """Compute exponent of prime p in N! via repeated division."""
    e = 0
    while N:
        N //= p
        e += N
    return e

def L_of_N(N):
    """Compute L(N) = ln(ln N)*[1 - (1/N) * sum_{2p≤N} floor(v_p(N!)/ceil(log_p(N)))]."""
    # 1) generate primes up to N//2
    primes = sieve(N//2)
    
    total = 0
    lnN = math.log(N)
    for p in primes:
        if 2*p > N:
            break
        # exponent of p in N!
        vp = v_p_factorial(N, p)
        # ceil(log base p of N)
        # avoid repeated logs:
        ceil_log_p = math.ceil(lnN / math.log(p))
        total += vp // ceil_log_p
    
    return math.log(lnN) * (1 - total / N)

if __name__ == "__main__":
    N = 10 ** 5
    print(f"L({N}) =", L_of_N(N))
