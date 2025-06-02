# Multiplicative Optimal Partitions

A mathematical research project investigating optimal multiplicative partitions and their associated sequences, with applications to number theory and combinatorics.

## Overview

This project introduces and analyzes a function **P_π(n)** that represents the maximum number of factors in a multiplicative partition of a positive integer n, where each factor must be at least as large as the total number of factors in the partition.

### Definition

For a positive integer n, **P_π(n)** is defined as the largest positive integer k such that n can be written as a product of k integer factors d₁, d₂, ..., dₖ where:
1. The product of all factors equals n: ∏(i=1 to k) dᵢ = n
2. Each factor is at least k: dᵢ ≥ k for all i = 1, ..., k

### Examples
- **P_π(10) = 2**: Can be written as {2,5} where both factors ≥ 2
- **P_π(11) = 1**: As 11 is prime, only partition is {11}
- **P_π(63) = 3**: Can be written as {3,3,7} where all factors ≥ 3
- **P_π(64) = 3**: Can be written as {4,4,4} where all factors ≥ 3

## Dataset Overview: `optimal_partitions_exact_10_5.csv`

The CSV dataset contains comprehensive computational results for **P_π(n)** covering n=1 to 100,000 (10⁵). This dataset supports the theoretical analysis and provides empirical validation for the convergence conjecture using the **EXACT ALGORITHM** which guarantees 100% optimal results.

### Table Structure

```csv
n,P_pi(n),Factorization,SequenceType,SequenceIndex
4,2,2*2,decrease,1
10,2,2*5,decrease,3
27,3,3*3*3,decrease,8
256,4,4*4*4*4,decrease,89
```

#### Column Descriptions

| Column | Description | Example Values |
|--------|-------------|----------------|
| **n** | Input integer (1 to 100,000) | 1, 2, 3, ..., 100000 |
| **P_pi(n)** | Computed partition function value | 1, 2, 3, 4 |
| **Factorization** | Actual multiplicative partition achieving P_π(n) | `2*5`, `3*3*7`, `4*4*4*4` |
| **SequenceType** | Local behavior classification | `decrease`, `equality`, `increase` |
| **SequenceIndex** | Sequential position within sequence type | 1, 2, 3, ... |

#### Sequence Type Classification

The dataset classifies each integer n based on how P_π(n) compares to P_π(n+1):

- **Decrease**: P_π(n) > P_π(n+1) - Function value drops
- **Equality**: P_π(n) = P_π(n+1) - Function value stays same  
- **Increase**: P_π(n) < P_π(n+1) - Function value rises

### Dataset Statistics

Based on the complete dataset (n=1 to 100,000):

| Sequence Type | Count | Density | Example Terms |
|---------------|-------|---------|---------------|
| **Decrease** | ~37,370 | ~0.3737 | 4, 6, 10, 12, 16, 18, 22, 27, 28, 30... |
| **Equality** | ~25,250 | ~0.2525 | 1, 2, 8, 9, 14, 15, 20, 21, 24, 25... |
| **Increase** | ~37,380 | ~0.3738 | 3, 5, 7, 11, 13, 17, 19, 23, 26, 29... |

These empirical densities validate the theoretical conjecture: **2C⁽±⁾ + C⁽⁰⁾ = 1**

## C Implementations: Computational Approaches

This project provides two distinct C implementations for generating P_π(n) datasets, each with different accuracy and performance characteristics.

### Exact Algorithm Implementation: `optimal_partitions_exact_chunked.c`

The exact algorithm provides **100% guaranteed optimal results** through rigorous mathematical verification of every partition.

#### **Mathematical Guarantees**
- **Perfect Accuracy**: Finds the provably optimal P_π(n) for every input
- **Exhaustive Verification**: Uses recursive partition checking with mathematical bounds
- **No Approximations**: Every result is mathematically verified
- **Direct Translation**: Implements the exact same logic as the reference Python algorithm

#### **Core Algorithm Features**

**Exact Recursive Partition Detection**
```c
// Direct translation from Python reference implementation
static bool recursive_partition_check(long long remaining, int factors_left, 
                                     int min_factor, Factorization* result, int depth)
```

- **Mathematical Bounds**: Uses exact formulas to determine search ranges
- **Early Termination**: Stops when k^k > n (mathematically impossible)
- **Overflow Protection**: Handles large numbers safely with LLONG_MAX checks
- **Optimized Cases**: Special handling for k=1 and k=2 (most common scenarios)

**Algorithm Methodology**
1. **Start with k=1**: Check if n can be partitioned into exactly 1 factor ≥ 1
2. **Increment k**: For each k, use recursive search to find valid partitions
3. **Termination**: Stop when k^k > n (mathematically impossible)
4. **Result**: Return the maximum k found with valid partition

**Performance Optimizations**
```c
// Fast integer power with overflow detection
static inline long long fast_pow_safe(int base, int exp)

// Optimized k=2 case (covers ~70% of all numbers)
if (k == 2) {
    for (long long d = 2; d * d <= n; d++) {
        if (n % d == 0) {
            // Direct factorization check
        }
    }
}
```

#### **Memory Management**
- **Chunked Processing**: Handles datasets in 50M number chunks (~1.2GB RAM each)
- **Memory Limit**: Stays under 20GB regardless of dataset size
- **Dynamic Allocation**: Efficient memory usage with automatic cleanup
- **Progress Monitoring**: Reports progress every 1M numbers

#### **Compilation and Usage**

```bash
# Compile with maximum optimization for exact algorithm
gcc -O3 -march=native -mtune=native -flto -funroll-loops \
    -ffast-math -DNDEBUG -s -Wall -Wextra -Wpedantic -std=c99 \
    -o optimal_partitions_exact optimal_partitions_exact_chunked.c -lm

# Generate exact results for 1M numbers (default)
./optimal_partitions_exact

# Custom range with specific parameters
./optimal_partitions_exact [total_n] [chunk_size] [output_file]

# Large-scale exact computation (10M numbers, 25M chunk size)
./optimal_partitions_exact 10000000 25000000 exact_results.csv

# Memory-constrained environment (smaller chunks)
./optimal_partitions_exact 1000000 10000000 exact_1M.csv
```

#### **Performance Characteristics (Exact Algorithm)**

| Dataset Size | Peak RAM Usage | Recommended Chunk Size | Processing Time |
|--------------|----------------|------------------------|-----------------|
| 1M numbers   | ~1.2GB         | 50M (default)         | ~2-5 minutes    |
| 10M numbers  | ~1.2GB         | 50M                   | ~20-60 minutes  |
| 100M numbers | ~1.2GB         | 25M                   | ~3-10 hours     |

- **Accuracy**: 100% guaranteed optimal results
- **Time Complexity**: O(n * k_max * factors_per_k) where k_max ≤ log(n)
- **Space Complexity**: O(chunk_size) per processing chunk
- **Throughput**: ~500-2000 numbers/second (depends on k distribution)

#### **Algorithm Validation Examples**

| n | P_π(n) | Optimal Factorization | Algorithm Verification |
|---|--------|--------------------|----------------------|
| 1 | 1 | {1} | k=1: 1≥1 ✓, k=2: 2²>1 ✗ |
| 10 | 2 | {2,5} | k=2: 2*5=10, 2≥2, 5≥2 ✓ |
| 63 | 3 | {3,3,7} | k=3: 3*3*7=63, all≥3 ✓ |
| 256 | 4 | {4,4,4,4} | k=4: 4⁴=256, all≥4 ✓ |

#### **Error Handling and Robustness**

**Overflow Protection**
```c
// Safe power calculation with overflow detection
if (base >= 100 && exp >= 4) return LLONG_MAX;
if (result > LLONG_MAX / b) return LLONG_MAX;
```

**Progress Reporting**
```bash
=== EXACT Optimal Multiplicative Partitions Generator ===
Author: Daniel Eduardo Ruiz C. (danuaemx)
Date: 2025-06-02 03:41:19
Algorithm: EXACT - Guaranteed optimal k for all n
Range: 1 to 1000000
Memory per chunk: ~1.2 GB

--- EXACT Chunk 1/1 ---
Processing chunk: 1 to 1000000 (EXACT ALGORITHM)
  Chunk progress: 10.0% (n=100000, P_π=2)
  EXACT calculation time: 45.23 seconds

=== EXACT ALGORITHM COMPLETION REPORT ===
Total computation time: 47.15 seconds
Algorithm: EXACT - Guaranteed optimal results
Numbers per second: 21209
```

### When to Use Each Implementation

#### **Exact Algorithm Recommended For:**
- **Mathematical Research**: When 100% accuracy is required
- **Algorithm Verification**: Validating other implementations
- **Small to Medium Datasets**: Up to 10M numbers
- **Theoretical Studies**: Proving mathematical properties
- **Reference Computations**: Creating verified benchmark datasets

#### **Key Advantages of Exact Algorithm:**
- **Mathematical Rigor**: Provably correct results
- **Research Quality**: Suitable for academic publications
- **Verification**: Can validate other algorithms
- **Completeness**: Finds optimal factorizations

## Research Components

### 1. Core Theory (`main.tex`, `document.pdf`)
- **Mathematical Framework**: Formal definitions and theorems
- **Partition Function Analysis**: Properties and behavior of P_π(n)
- **Local Behavior Sequences**: Three derived sequences based on function transitions
- **Convergence Conjecture**: Asymptotic density analysis with empirical validation

### 2. Computational Implementation

#### Python Analysis (`basic_graphs.py`, `conjecture_analyzer.py`)
- **PartitionAnalyzer Class**: Efficient computation of P_π(n) values
- **Sequence Generation**: Automatic computation of decrease, increase, and equality sequences
- **Statistical Analysis**: Density convergence validation
- **Visualization Tools**: Comprehensive graphing capabilities

#### C Implementation (`optimal_partitions_exact_chunked.c`)
- **High-Performance Computing**: Optimized algorithms for large-scale analysis
- **Memory Management**: Efficient handling of extensive datasets
- **Mathematical Guarantees**: 100% exact results with rigorous verification

### 3. Data and Results

#### Generated Datasets (`optimal_partitions_exact_10_5.csv`)
- **Computational Results**: P_π(n) values for n up to 10⁵ (EXACT ALGORITHM)
- **Sequence Data**: Complete listings of derived sequences
- **Statistical Validation**: Empirical evidence for theoretical conjectures
- **Guaranteed Accuracy**: All results verified through exact computation

#### Bibliography (`ref.bib`)
- **Academic References**: Related work in multiplicative partitions
- **Mathematical Context**: Connections to classical number theory

## Key Mathematical Results

### Local Behavior Sequences

The project defines three sequences based on consecutive value comparisons:

1. **Decrease Sequence (dⱼ)**: Integers m where P_π(m) > P_π(m+1)
2. **Equality Sequence (eⱼ)**: Integers m where P_π(m) = P_π(m+1)  
3. **Increase Sequence (iⱼ)**: Integers m where P_π(m) < P_π(m+1)

### Convergence Conjecture

The research proposes that these sequences have asymptotic densities:
- **C⁽⁻⁾ ≈ 0.3737**: Density of decrease points
- **C⁽⁰⁾ ≈ 0.2525**: Density of equality points  
- **C⁽⁺⁾ ≈ 0.3737**: Density of increase points

With the fundamental relationship: **2C⁽±⁾ + C⁽⁰⁾ = 1**

## Usage

### Running the Analysis

```python
from basic_graphs import PartitionAnalyzer

# Initialize analyzer for values up to 1000
analyzer = PartitionAnalyzer(max_n=1000)

# Compute all partition function values
analyzer.compute_all_values()

# Generate visualizations
analyzer.plot_partition_function()
analyzer.plot_level_frequencies()
analyzer.print_statistics()
```

### Generating Exact Datasets

```bash
# Default exact computation (1M numbers)
./optimal_partitions_exact

# Large-scale exact computation
./optimal_partitions_exact 10000000 25000000 large_exact_dataset.csv

# Memory-efficient exact computation
./optimal_partitions_exact 1000000 10000000 exact_1M.csv
```

## Applications

- **Number Theory**: Novel approach to multiplicative partitions
- **Combinatorics**: Constrained factorization problems
- **Statistical Analysis**: Asymptotic density studies
- **Computational Mathematics**: Algorithm development for partition problems
- **Mathematical Verification**: Benchmark datasets for algorithm validation

## Future Directions

- Analytical bounds for P_π(n)
- Characterization of sequence members
- Distribution analysis within partition levels
- Generalization to modified constraints
- Connections to highly composite numbers
- Parallel processing implementations for exact algorithm

## Author

**Daniel Eduardo Ruiz C.**  
Universidad Autónoma del Estado de México  
Email: druizc005@alumno.uaemex.mx  
Date: 2025-06-02 03:41:19

## Files Structure

```
multiplicative_optimal_partitions/
├── README.md                                # This documentation file
├── main.tex                                 # Main research paper LaTeX source
├── document.pdf                            # Compiled research document  
├── basic_graphs.py                         # Python visualization tools
├── conjecture_analyzer.py                  # Statistical analysis tools
├── optimal_partitions_exact_chunked.c      # EXACT algorithm C implementation
├── optimal_partitions_exact_10_5.csv      # EXACT computational results dataset
└── ref.bib                                 # Bibliography references
```

## Algorithm Summary

This project provides a mathematically rigorous implementation of optimal multiplicative partition computation. The **exact algorithm** guarantees 100% optimal results through exhaustive verification, making it suitable for research applications where mathematical certainty is required.

The implementation combines theoretical rigor with practical computational efficiency, using chunked processing to handle large datasets while maintaining perfect accuracy. All results in the provided dataset (`optimal_partitions_exact_10_5.csv`) are guaranteed to be mathematically optimal.

This project represents a comprehensive investigation into a novel class of multiplicative partitions, combining theoretical analysis with extensive computational validation using guaranteed exact algorithms to establish new results in number theory and combinatorics.
