import math
import sys

def sieve(n):
    """
    Return list of all primes ≤ n via a Sieve of Eratosthenes
    using slicing for speed.
    """
    is_comp = bytearray(b'\x00')*(n+1)
    primes = []
    for i in range(2, n+1):
        if not is_comp[i]:
            primes.append(i)
            start = i*i
            if start <= n:
                is_comp[start:n+1:i] = b'\x01'*(((n - start)//i) + 1)
    return primes

def v_p_factorial(N, p):
    """
    Exponent of prime p in N! via repeated integer division.
    """
    count = 0
    while N:
        N //= p
        count += N
    return count

def Y_of_N(N):
    """
    Compute Y(N) = (1/N) * sum_{2p ≤ N} [v_p(N!) mod ceil(log_p N)] * ln(p).
    """
    limit = N // 2
    primes = sieve(limit)
    lnN = math.log(N)
    total = 0.0

    for p in primes:
        if p*2 > N:
            break
        vp = v_p_factorial(N, p)
        ceil_log_p = math.ceil(lnN / math.log(p))
        total += (vp % ceil_log_p) * math.log(p)

    return total / N

if __name__ == "__main__":
    N = 10**5
    print(f"Y({N}) =", Y_of_N(N))
