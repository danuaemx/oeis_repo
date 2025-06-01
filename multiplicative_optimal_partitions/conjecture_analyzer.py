import numpy as np
import matplotlib.pyplot as plt
from functools import lru_cache
from typing import List, Dict, Tuple
import math
import random
from collections import defaultdict

class StatisticalConjectureAnalyzer:
    def __init__(self, max_n: int = 1000000):
        self.max_n = max_n
        self.partition_values = {}
        self.decrease_seq = []
        self.increase_seq = []
        self.equality_seq = []
        
    @lru_cache(maxsize=None)
    def get_divisors(self, n: int) -> List[int]:
        """Get all divisors of n efficiently."""
        divisors = []
        for i in range(1, int(math.sqrt(n)) + 1):
            if n % i == 0:
                divisors.append(i)
                if i != n // i:
                    divisors.append(n // i)
        return sorted(divisors)
    
    def can_partition_with_k_factors(self, n: int, k: int) -> bool:
        """Check if n can be partitioned into k factors, each >= k."""
        if k == 1:
            return n >= 1
        
        if k ** k > n:
            return False
            
        if k == 2:
            divisors = self.get_divisors(n)
            for d in divisors:
                if d >= 2 and n // d >= 2:
                    return True
            return False
        
        return self._recursive_partition_check(n, k, k)
    
    def _recursive_partition_check(self, remaining: int, factors_left: int, min_factor: int) -> bool:
        """Recursively check if remaining can be partitioned."""
        if factors_left == 0:
            return remaining == 1
        
        if factors_left == 1:
            return remaining >= min_factor
        
        if min_factor ** factors_left > remaining:
            return False
        
        max_factor = min(remaining // (min_factor ** (factors_left - 1)), 
                        int(remaining ** (1.0 / factors_left)) + 1)
        
        for factor in range(min_factor, max_factor + 1):
            if remaining % factor == 0:
                if self._recursive_partition_check(remaining // factor, factors_left - 1, min_factor):
                    return True
        
        return False
    
    @lru_cache(maxsize=None)
    def partition_function(self, n: int) -> int:
        """Calculate P_π(n)."""
        if n == 1:
            return 1
        
        max_k = 1
        k = 1
        
        while k ** k <= n:
            if self.can_partition_with_k_factors(n, k):
                max_k = k
            k += 1
        
        return max_k
    
    def compute_sequences(self):
        """Compute partition function values and sequences up to max_n."""
        print(f"Computing partition function for n = 1 to {self.max_n}...")
        print("This may take several hours for large values...")
        
        # Batch processing for memory efficiency
        batch_size = 10000
        for start in range(1, self.max_n + 1, batch_size):
            end = min(start + batch_size - 1, self.max_n)
            print(f"Processing batch: {start} to {end}")
            
            for n in range(start, end + 1):
                if n % 10000 == 0:
                    print(f"Progress: {n}/{self.max_n}")
                self.partition_values[n] = self.partition_function(n)
        
        print("Computing sequences...")
        for m in range(1, self.max_n):
            if m % 50000 == 0:
                print(f"Sequence progress: {m}/{self.max_n}")
                
            p_m = self.partition_values[m]
            p_m_plus_1 = self.partition_values[m + 1]
            
            if p_m > p_m_plus_1:
                self.decrease_seq.append(m)
            elif p_m < p_m_plus_1:
                self.increase_seq.append(m)
            else:
                self.equality_seq.append(m)
    
    def generate_statistical_M_values(self) -> List[int]:
        """Generate M values with statistical sampling between powers of 10."""
        M_values = []
        random.seed(42)  # For reproducibility
        
        # Add exact powers of 10
        powers_of_10 = [10**i for i in range(2, 7)]  # 10^2 to 10^6
        M_values.extend(powers_of_10)
        
        # Add random samples between consecutive powers of 10
        for i in range(2, 6):  # Between 10^2 and 10^6
            lower = 10**i
            upper = 10**(i+1)
            
            # Generate random samples in this range
            n_samples = 8  # Number of random samples per decade
            samples = []
            for _ in range(n_samples):
                # Use log-uniform distribution for better coverage
                log_lower = math.log10(lower)
                log_upper = math.log10(upper)
                log_sample = random.uniform(log_lower, log_upper)
                sample = int(10**log_sample)
                samples.append(sample)
            
            # Remove duplicates and sort
            samples = sorted(list(set(samples)))
            M_values.extend(samples)
        
        # Add some specific intermediate values for better coverage
        additional_values = [
            150, 250, 350, 750,  # Around 10^2
            1500, 2500, 3500, 7500,  # Around 10^3
            15000, 25000, 35000, 75000,  # Around 10^4
            150000, 250000, 350000, 750000,  # Around 10^5
        ]
        M_values.extend(additional_values)
        
        # Remove duplicates, sort, and filter to be within our computed range
        M_values = sorted(list(set(M_values)))
        M_values = [m for m in M_values if m <= self.max_n - 1]  # -1 because we need m+1
        
        return M_values
    
    def find_j_M(self, sequence: List[int], M: int) -> int:
        """Find j_M = max{j : sequence[j-1] <= M}"""
        count = 0
        for val in sequence:
            if val <= M:
                count += 1
            else:
                break
        return count
    
    def compute_conjecture_values(self, M_values: List[int]) -> List[Dict]:
        """Compute conjecture values for given M values."""
        results = []
        
        print(f"Computing conjecture values for {len(M_values)} M values...")
        
        for i, M in enumerate(M_values):
            if i % 10 == 0:
                print(f"Processing M value {i+1}/{len(M_values)}: M = {M}")
                
            # Find j_M values
            j_minus_M = self.find_j_M(self.decrease_seq, M)
            j_zero_M = self.find_j_M(self.equality_seq, M)
            j_plus_M = self.find_j_M(self.increase_seq, M)
            
            # Get corresponding sequence values
            d_j_minus = self.decrease_seq[j_minus_M - 1] if j_minus_M > 0 else 0
            e_j_zero = self.equality_seq[j_zero_M - 1] if j_zero_M > 0 else 0
            i_j_plus = self.increase_seq[j_plus_M - 1] if j_plus_M > 0 else 0
            
            # Compute ratios
            C_minus = j_minus_M / d_j_minus if d_j_minus > 0 else 0
            C_zero = j_zero_M / e_j_zero if e_j_zero > 0 else 0
            C_plus = j_plus_M / i_j_plus if i_j_plus > 0 else 0
            
            # Compute differences |M - s_M|
            diff_minus = abs(M - d_j_minus) if d_j_minus > 0 else float('inf')
            diff_zero = abs(M - e_j_zero) if e_j_zero > 0 else float('inf')
            diff_plus = abs(M - i_j_plus) if i_j_plus > 0 else float('inf')
            
            results.append({
                'M': M,
                'j_minus_M': j_minus_M,
                'd_j_minus': d_j_minus,
                'j_zero_M': j_zero_M,
                'e_j_zero': e_j_zero,
                'j_plus_M': j_plus_M,
                'i_j_plus': i_j_plus,
                'C_minus': C_minus,
                'C_zero': C_zero,
                'C_plus': C_plus,
                'diff_minus': diff_minus,
                'diff_zero': diff_zero,
                'diff_plus': diff_plus
            })
        
        return results
    
    def generate_latex_table(self, results: List[Dict], filename: str = "statistical_conjecture_table.tex"):
        """Generate LaTeX tables for statistical conjecture analysis."""
        
        latex_content = r"""
\begin{table}[h]
\centering
\caption{Statistical Convergence Analysis of the Conjecture for Various Values of $M$ up to $10^6$}
\label{tab:statistical_conjecture_analysis}
\resizebox{\textwidth}{!}{%
\begin{tabular}{|c|c|c|c|c|c|c|c|c|c|}
\hline
$M$ & $j^{(-)}_M$ & $d_{j^{(-)}_M}$ & $j^{(0)}_M$ & $e_{j^{(0)}_M}$ & $j^{(+)}_M$ & $i_{j^{(+)}_M}$ & $C^{(-)}$ & $C^{(0)}$ & $C^{(+)}$ \\
\hline
"""
        
        for result in results:
            M = result['M']
            j_minus = result['j_minus_M']
            d_j_minus = result['d_j_minus']
            j_zero = result['j_zero_M']
            e_j_zero = result['e_j_zero']
            j_plus = result['j_plus_M']
            i_j_plus = result['i_j_plus']
            C_minus = result['C_minus']
            C_zero = result['C_zero']
            C_plus = result['C_plus']
            
            # Format M with scientific notation for large numbers
            if M >= 100000:
                M_str = f"{M:.0e}"
            else:
                M_str = str(M)
            
            latex_content += f"{M_str} & {j_minus} & {d_j_minus} & {j_zero} & {e_j_zero} & {j_plus} & {i_j_plus} & "
            
            if C_minus > 0:
                latex_content += f"{C_minus:.6f} & "
            else:
                latex_content += "--- & "
                
            if C_zero > 0:
                latex_content += f"{C_zero:.6f} & "
            else:
                latex_content += "--- & "
                
            if C_plus > 0:
                latex_content += f"{C_plus:.6f} \\\\\n"
            else:
                latex_content += "--- \\\\\n"
            
            latex_content += "\\hline\n"
        
        latex_content += r"""
\end{tabular}%
}
\end{table}

\begin{table}[h]
\centering
\caption{Statistical Conjecture Relation Analysis: $2C^{(\pm)} + C^{(0)} = 1$}
\label{tab:statistical_conjecture_relation}
\resizebox{\textwidth}{!}{%
\begin{tabular}{|c|c|c|c|c|c|c|c|}
\hline
$M$ & $C^{(-)}$ & $C^{(0)}$ & $C^{(+)}$ & $2C^{(-)}$ & $2C^{(-)} + C^{(0)}$ & $2C^{(+)} + C^{(0)}$ & $\left|1 - (2C^{(-)} + C^{(0)})\right|$ \\
\hline
"""
        
        for result in results:
            M = result['M']
            C_minus = result['C_minus']
            C_zero = result['C_zero']
            C_plus = result['C_plus']
            
            # Format M with scientific notation for large numbers
            if M >= 100000:
                M_str = f"{M:.0e}"
            else:
                M_str = str(M)
            
            if C_minus > 0 and C_zero > 0:
                term1 = 2 * C_minus
                sum_minus = term1 + C_zero
                error_minus = abs(1 - sum_minus)
                
                if C_plus > 0:
                    sum_plus = 2 * C_plus + C_zero
                else:
                    sum_plus = float('nan')
                
                latex_content += f"{M_str} & {C_minus:.6f} & {C_zero:.6f} & "
                if C_plus > 0:
                    latex_content += f"{C_plus:.6f} & "
                else:
                    latex_content += "--- & "
                latex_content += f"{term1:.6f} & {sum_minus:.6f} & "
                if not math.isnan(sum_plus):
                    latex_content += f"{sum_plus:.6f} & "
                else:
                    latex_content += "--- & "
                latex_content += f"{error_minus:.6f} \\\\\n"
            else:
                latex_content += f"{M_str} & "
                if C_minus > 0:
                    latex_content += f"{C_minus:.6f} & "
                else:
                    latex_content += "--- & "
                if C_zero > 0:
                    latex_content += f"{C_zero:.6f} & "
                else:
                    latex_content += "--- & "
                if C_plus > 0:
                    latex_content += f"{C_plus:.6f} & "
                else:
                    latex_content += "--- & "
                latex_content += "--- & --- & --- & --- \\\\\n"
            
            latex_content += "\\hline\n"
        
        latex_content += r"""
\end{tabular}%
}
\end{table}

\begin{table}[h]
\centering
\caption{Statistical Analysis of Differences $|M - s_M|$ for Convergence}
\label{tab:statistical_differences_analysis}
\resizebox{\textwidth}{!}{%
\begin{tabular}{|c|c|c|c|c|c|c|}
\hline
$M$ & $|M - d_{j^{(-)}_M}|$ & $|M - e_{j^{(0)}_M}|$ & $|M - i_{j^{(+)}_M}|$ & $\frac{|M - d_{j^{(-)}_M}|}{M}$ & $\frac{|M - e_{j^{(0)}_M}|}{M}$ & $\frac{|M - i_{j^{(+)}_M}|}{M}$ \\
\hline
"""
        
        for result in results:
            M = result['M']
            diff_minus = result['diff_minus']
            diff_zero = result['diff_zero']
            diff_plus = result['diff_plus']
            
            # Format M with scientific notation for large numbers
            if M >= 100000:
                M_str = f"{M:.0e}"
            else:
                M_str = str(M)
            
            rel_diff_minus = diff_minus / M if diff_minus != float('inf') else float('inf')
            rel_diff_zero = diff_zero / M if diff_zero != float('inf') else float('inf')
            rel_diff_plus = diff_plus / M if diff_plus != float('inf') else float('inf')
            
            latex_content += f"{M_str} & "
            
            if diff_minus != float('inf'):
                latex_content += f"{diff_minus} & "
            else:
                latex_content += "--- & "
                
            if diff_zero != float('inf'):
                latex_content += f"{diff_zero} & "
            else:
                latex_content += "--- & "
                
            if diff_plus != float('inf'):
                latex_content += f"{diff_plus} & "
            else:
                latex_content += "--- & "
            
            if rel_diff_minus != float('inf'):
                latex_content += f"{rel_diff_minus:.6f} & "
            else:
                latex_content += "--- & "
                
            if rel_diff_zero != float('inf'):
                latex_content += f"{rel_diff_zero:.6f} & "
            else:
                latex_content += "--- & "
                
            if rel_diff_plus != float('inf'):
                latex_content += f"{rel_diff_plus:.6f} \\\\\n"
            else:
                latex_content += "--- \\\\\n"
            
            latex_content += "\\hline\n"
        
        latex_content += r"""
\end{tabular}%
}
\end{table}
"""
        
        with open(filename, 'w') as f:
            f.write(latex_content)
        
        print(f"LaTeX tables saved to {filename}")
        return latex_content
    
    def save_sequences(self, filename: str = "sequences_data.txt"):
        """Save computed sequences to file for later analysis."""
        with open(filename, 'w') as f:
            f.write(f"Computed up to n = {self.max_n}\n")
            f.write(f"Decrease sequence length: {len(self.decrease_seq)}\n")
            f.write(f"Equality sequence length: {len(self.equality_seq)}\n")
            f.write(f"Increase sequence length: {len(self.increase_seq)}\n\n")
            
            f.write("Decrease sequence (first 100):\n")
            f.write(str(self.decrease_seq[:100]) + "\n\n")
            
            f.write("Equality sequence (first 100):\n")
            f.write(str(self.equality_seq[:100]) + "\n\n")
            
            f.write("Increase sequence (first 100):\n")
            f.write(str(self.increase_seq[:100]) + "\n")

def main():
    # Configuration for statistical analysis up to 10^6
    max_n = 1000000  # 10^6
    
    print("Statistical Conjecture Analyzer")
    print(f"Computing up to n = {max_n:,}")
    print("This will take significant time and memory...")
    
    # Create analyzer and compute sequences
    analyzer = StatisticalConjectureAnalyzer(max_n)
    analyzer.compute_sequences()
    
    # Save sequences for future reference
    analyzer.save_sequences()
    
    print(f"\nSequence statistics:")
    print(f"Decrease sequence: {len(analyzer.decrease_seq):,} terms")
    print(f"Equality sequence: {len(analyzer.equality_seq):,} terms")
    print(f"Increase sequence: {len(analyzer.increase_seq):,} terms")
    
    # Generate statistical M values
    M_values = analyzer.generate_statistical_M_values()
    print(f"\nGenerated {len(M_values)} M values for analysis")
    print(f"M values range: {min(M_values)} to {max(M_values):,}")
    
    # Compute conjecture values
    results = analyzer.compute_conjecture_values(M_values)
    
    # Generate LaTeX tables
    latex_content = analyzer.generate_latex_table(results)
    
    # Print summary statistics
    print("\nStatistical Summary:")
    print("M\t\tC^(-)\t\tC^(0)\t\tC^(+)\t\t2C^(-) + C^(0)")
    print("-" * 80)
    
    # Group results by order of magnitude for statistical analysis
    by_magnitude = defaultdict(list)
    for result in results:
        magnitude = int(math.log10(result['M']))
        by_magnitude[magnitude].append(result)
    
    for magnitude in sorted(by_magnitude.keys()):
        magnitude_results = by_magnitude[magnitude]
        print(f"\nOrder of magnitude 10^{magnitude}:")
        
        for result in magnitude_results:
            M = result['M']
            C_minus = result['C_minus']
            C_zero = result['C_zero']
            C_plus = result['C_plus']
            
            if C_minus > 0 and C_zero > 0:
                relation_value = 2*C_minus + C_zero
                print(f"{M:8,}\t{C_minus:.6f}\t{C_zero:.6f}\t{C_plus:.6f}\t{relation_value:.6f}")
    
    print(f"\nAnalysis complete. Results saved to statistical_conjecture_table.tex")

if __name__ == "__main__":
    main()
