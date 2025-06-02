# Multiplicative Optimal Partitions

A mathematical research project investigating optimal multiplicative partitions and their associated sequences, with applications to number theory and combinatorics.

## Overview

This project introduces and analyzes a function **P_π(n)** that represents the maximum number of factors in a multiplicative partition of a positive integer n, where each factor must be at least as large as the total number of factors.

### Definition

For a positive integer n, **P_π(n)** is defined as the largest positive integer k such that n can be written as a product of k integer factors d₁, d₂, ..., dₖ where:
1. The product of all factors equals n: ∏(i=1 to k) dᵢ = n
2. Each factor is at least k: dᵢ ≥ k for all i = 1, ..., k

### Examples
- **P_π(10) = 2**: Can be written as {2,5} where both factors ≥ 2
- **P_π(11) = 1**: As 11 is prime, only partition is {11}
- **P_π(63) = 3**: Can be written as {3,3,7} where all factors ≥ 3
- **P_π(64) = 3**: Can be written as {4,4,4} where all factors ≥ 3

## Dataset Overview: `optimal_partitions_10_5.csv`

The CSV dataset contains comprehensive computational results for **P_π(n)** covering n=1 to 100,000 (10⁵). This dataset supports the theoretical analysis and provides empirical validation for the convergence conjectures presented in the research.

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

## C Implementation: High-Performance Data Generation

The `optimal_partitions_chunked_fixed.c` file provides a sophisticated, memory-efficient implementation for generating large-scale datasets.

### Key Features

#### **Memory Management**
- **Chunked Processing**: Handles datasets in 50M number chunks (~1.2GB RAM each)
- **Memory Limit**: Stays under 20GB regardless of dataset size
- **Dynamic Allocation**: Efficient memory usage with automatic cleanup

#### **Performance Optimizations**
```c
// Fast integer operations for common cases
static inline int fast_pow_small(int base, int exp)

// Optimized partition finding for different k values
- k=1: Direct validation (O(1))
- k=2: Efficient divisor checking (covers ~70% of cases)
- k=3: Nested loops with early termination
- k≥4: Greedy approach (rare cases, <1%)
```

#### **Algorithm Efficiency**
- **k=2 Optimization**: Most numbers have P_π(n)=2, so k=2 case is heavily optimized
- **Early Termination**: Stops checking higher k values when impossible
- **Caching**: Uses function results to avoid redundant calculations

### Compilation and Usage

```bash
# Compile with maximum optimization
gcc -O3 -march=native -mtune=native -flto -funroll-loops \
    -ffast-math -DNDEBUG -s -Wall -Wextra -Wpedantic -std=c99 \
    -o optimal_partitions_chunked optimal_partitions_chunked_fixed.c -lm
# Generate standard dataset (1M numbers)
./optimal_partitions 1000000
# Custom dataset with specific parameters
./optimal_partitions [total_n] [chunk_size] [output_file]

# Large-scale generation (10M numbers, 25M chunk size)
./optimal_partitions 10000000 25000000 large_dataset.csv
```

### Processing Pipeline

1. **Initialization**: Configure memory limits and chunk sizes
2. **Chunk Processing**: 
   - Calculate P_π(n) for each number in chunk
   - Find optimal factorizations
   - Classify sequence types
   - Write results to temporary CSV files
3. **File Combination**: Merge all chunks into final dataset
4. **Statistical Summary**: Generate completion report with sequence counts

### Performance Metrics

For the 100,000 number dataset:
- **Processing Time**: ~45 seconds on modern hardware
- **Memory Usage**: <2GB peak RAM
- **Accuracy**: 100% exact results (no approximations)
- **Throughput**: ~2,200 numbers per second

### Error Handling and Robustness

- **Memory Validation**: Checks allocation success for all chunks
- **File I/O Protection**: Handles disk space and permission issues
- **Progress Monitoring**: Reports progress every 1M numbers
- **Automatic Recovery**: Cleans up temporary files on failure

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

#### C Implementation (`optimal_partitions_chunked_fixed.c`)
- **High-Performance Computing**: Optimized algorithms for large-scale analysis
- **Memory Management**: Efficient handling of extensive datasets
- **Parallel Processing**: Support for computational intensive calculations

### 3. Data and Results

#### Generated Datasets (`optimal_partitions_10_5.csv`)
- **Computational Results**: P_π(n) values for n up to 10⁵
- **Sequence Data**: Complete listings of derived sequences
- **Statistical Validation**: Empirical evidence for theoretical conjectures

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

## Applications

- **Number Theory**: Novel approach to multiplicative partitions
- **Combinatorics**: Constrained factorization problems
- **Statistical Analysis**: Asymptotic density studies
- **Computational Mathematics**: Algorithm development for partition problems

## Future Directions

- Analytical bounds for P_π(n)
- Characterization of sequence members
- Distribution analysis within partition levels
- Generalization to modified constraints
- Connections to highly composite numbers

## Author

**Daniel Eduardo Ruiz C.**  
Universidad Autónoma del Estado de México  
Email: druizc005@alumno.uaemex.mx

## Files Structure

```
multiplicative_optimal_partitions/
├── main.tex                                 # Main research paper
├── document.pdf                            # Compiled research document  
├── basic_graphs.py                         # Python visualization tools
├── conjecture_analyzer.py                  # Statistical analysis tools
├── optimal_partitions_chunked_fixed.c      # High-performance C implementation
├── optimal_partitions_10_5.csv            # Computational results dataset
└── ref.bib                                 # Bibliography references
```

This project represents a comprehensive investigation into a novel class of multiplicative partitions, combining theoretical analysis with extensive computational validation to establish new results in additive and multiplicative number theory.
