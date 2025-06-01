import numpy as np
import matplotlib.pyplot as plt
from functools import lru_cache
from typing import List, Dict
import math
from collections import defaultdict

class PartitionAnalyzer:
    def __init__(self, max_n: int = 1000):
        self.max_n = max_n
        self.partition_values = {}
        self.decrease_seq = []
        self.increase_seq = []
        self.equality_seq = []
        self.level_frequencies = defaultdict(lambda: {'decrease': 0, 'increase': 0, 'equality': 0})
        
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
    
    def compute_all_values(self):
        """Compute partition function values and sequences."""
        print(f"Computing partition function for n = 1 to {self.max_n}...")
        
        for n in range(1, self.max_n + 1):
            if n % 100 == 0:
                print(f"Progress: {n}/{self.max_n}")
            self.partition_values[n] = self.partition_function(n)
        
        for m in range(1, self.max_n):
            p_m = self.partition_values[m]
            p_m_plus_1 = self.partition_values[m + 1]
            
            if p_m > p_m_plus_1:
                self.decrease_seq.append(m)
                self.level_frequencies[p_m]['decrease'] += 1
            elif p_m < p_m_plus_1:
                self.increase_seq.append(m)
                self.level_frequencies[p_m]['increase'] += 1
            else:
                self.equality_seq.append(m)
                self.level_frequencies[p_m]['equality'] += 1
    
    def plot_partition_function(self):
        """Plot the partition function with marked transition points."""
        n_values = list(range(1, self.max_n + 1))
        p_values = [self.partition_values[n] for n in n_values]
        
        plt.figure(figsize=(12, 8))
        plt.plot(n_values, p_values, 'b-', linewidth=1, alpha=0.7)
        
        if self.decrease_seq:
            decrease_n = [n for n in self.decrease_seq if n <= self.max_n]
            decrease_p = [self.partition_values[n] for n in decrease_n]
            plt.scatter(decrease_n, decrease_p, color='red', s=20, alpha=0.6, label='Decrease')
        
        if self.increase_seq:
            increase_n = [n for n in self.increase_seq if n <= self.max_n]
            increase_p = [self.partition_values[n] for n in increase_n]
            plt.scatter(increase_n, increase_p, color='green', s=20, alpha=0.6, label='Increase')
        
        if self.equality_seq:
            equality_n = [n for n in self.equality_seq if n <= self.max_n]
            equality_p = [self.partition_values[n] for n in equality_n]
            plt.scatter(equality_n, equality_p, color='orange', s=15, alpha=0.6, label='Equality')
        
        plt.xlabel('n')
        plt.ylabel('P_π(n)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('partition_function.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_level_frequencies(self):
        """Plot frequency bar chart for each partition function level."""
        if not self.level_frequencies:
            return
        
        levels = sorted(self.level_frequencies.keys())
        decrease_counts = [self.level_frequencies[level]['decrease'] for level in levels]
        increase_counts = [self.level_frequencies[level]['increase'] for level in levels]
        equality_counts = [self.level_frequencies[level]['equality'] for level in levels]
        
        fig, ax = plt.subplots(figsize=(14, 8))
        x = np.arange(len(levels))
        width = 0.25
        
        bars1 = ax.bar(x - width, decrease_counts, width, label='Decrease', color='red', alpha=0.7)
        bars2 = ax.bar(x, increase_counts, width, label='Increase', color='green', alpha=0.7)
        bars3 = ax.bar(x + width, equality_counts, width, label='Equality', color='orange', alpha=0.7)
        
        def add_value_labels(bars):
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.annotate(f'{int(height)}',
                              xy=(bar.get_x() + bar.get_width() / 2, height),
                              xytext=(0, 3),
                              textcoords="offset points",
                              ha='center', va='bottom',
                              fontsize=8)
        
        add_value_labels(bars1)
        add_value_labels(bars2)
        add_value_labels(bars3)
        
        ax.set_xlabel('P_π(n) Level')
        ax.set_ylabel('Frequency')
        ax.set_xticks(x)
        ax.set_xticklabels(levels)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig('level_frequencies.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_decrease_sequence(self):
        """Plot the decrease sequence with ratios."""
        if not self.decrease_seq:
            return
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        j_values = list(range(1, len(self.decrease_seq) + 1))
        ax1.plot(j_values, self.decrease_seq, 'ro-', markersize=3, linewidth=1)
        ax1.set_xlabel('j')
        ax1.set_ylabel('d_j')
        ax1.grid(True, alpha=0.3)
        
        ratios = [d_j / j for j, d_j in enumerate(self.decrease_seq, 1)]
        ax2.plot(j_values, ratios, 'r-', linewidth=1)
        ax2.set_xlabel('j')
        ax2.set_ylabel('d_j / j')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('decrease_sequence.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_increase_sequence(self):
        """Plot the increase sequence with ratios."""
        if not self.increase_seq:
            return
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        j_values = list(range(1, len(self.increase_seq) + 1))
        ax1.plot(j_values, self.increase_seq, 'go-', markersize=3, linewidth=1)
        ax1.set_xlabel('j')
        ax1.set_ylabel('i_j')
        ax1.grid(True, alpha=0.3)
        
        ratios = [i_j / j for j, i_j in enumerate(self.increase_seq, 1)]
        ax2.plot(j_values, ratios, 'g-', linewidth=1)
        ax2.set_xlabel('j')
        ax2.set_ylabel('i_j / j')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('increase_sequence.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_equality_sequence(self):
        """Plot the equality sequence with ratios."""
        if not self.equality_seq:
            return
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        j_values = list(range(1, len(self.equality_seq) + 1))
        ax1.plot(j_values, self.equality_seq, 'o-', color='orange', markersize=3, linewidth=1)
        ax1.set_xlabel('j')
        ax1.set_ylabel('e_j')
        ax1.grid(True, alpha=0.3)
        
        ratios = [e_j / j for j, e_j in enumerate(self.equality_seq, 1)]
        ax2.plot(j_values, ratios, '-', color='orange', linewidth=1)
        ax2.set_xlabel('j')
        ax2.set_ylabel('e_j / j')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('equality_sequence.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def print_statistics(self):
        """Print statistics about the sequences."""
        print(f"\nStatistics for n = 1 to {self.max_n}:")
        print(f"Decrease sequence length: {len(self.decrease_seq)}")
        print(f"Increase sequence length: {len(self.increase_seq)}")
        print(f"Equality sequence length: {len(self.equality_seq)}")
        print(f"Total transitions: {len(self.decrease_seq) + len(self.increase_seq) + len(self.equality_seq)}")
        
        if self.decrease_seq:
            print(f"First 10 decrease terms: {self.decrease_seq[:10]}")
        if self.increase_seq:
            print(f"First 10 increase terms: {self.increase_seq[:10]}")
        if self.equality_seq:
            print(f"First 10 equality terms: {self.equality_seq[:10]}")
        
        print("\nFrequency by partition level:")
        for level in sorted(self.level_frequencies.keys()):
            freq = self.level_frequencies[level]
            total = freq['decrease'] + freq['increase'] + freq['equality']
            print(f"P_π(n) = {level}: Decrease={freq['decrease']}, Increase={freq['increase']}, Equality={freq['equality']}, Total={total}")

def main():
    max_n = 10000  # Adjust based on computational resources
    
    analyzer = PartitionAnalyzer(max_n)
    analyzer.compute_all_values()
    
    # Generate all individual image files
    print("\nGenerating graphs...")
    analyzer.plot_partition_function()
    print("Generated: partition_function.png")
    
    analyzer.plot_level_frequencies()
    print("Generated: level_frequencies.png")
    
    analyzer.plot_decrease_sequence()
    print("Generated: decrease_sequence.png")
    
    analyzer.plot_increase_sequence()
    print("Generated: increase_sequence.png")
    
    analyzer.plot_equality_sequence()
    print("Generated: equality_sequence.png")
    
    analyzer.print_statistics()

if __name__ == "__main__":
    main()
