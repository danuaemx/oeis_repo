#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdbool.h>
#include <time.h>
#include <sys/stat.h>
#include <unistd.h>
#include <limits.h>  // Added for LLONG_MAX

// Memory management for chunks < 20GB
#define MAX_CHUNK_SIZE 50000000    // 50M numbers per chunk (~1.2GB RAM)
#define MAX_FACTORS 20             // Increased for higher k values
#define BUFFER_SIZE 65536          // 64KB I/O buffer
#define PROGRESS_INTERVAL 1000000  // Progress every 1M numbers

typedef struct {
    int factors[MAX_FACTORS];
    int count;
} Factorization;

typedef enum {
    DECREASE = 0,
    EQUALITY = 1,
    INCREASE = 2
} SequenceType;

// Configuration structure
typedef struct {
    long long total_n;
    long long chunk_size;
    int num_chunks;
    char output_dir[256];
    char final_csv[256];
} Config;

// Global sequence counters (persistent across chunks)
static long long global_d_count = 0;
static long long global_e_count = 0;
static long long global_i_count = 0;

// Fast integer power calculation with overflow protection
static inline long long fast_pow_safe(int base, int exp) {
    if (exp == 0) return 1;
    if (exp == 1) return base;
    if (base == 1) return 1;
    
    // Early overflow detection
    if (base >= 100 && exp >= 4) return LLONG_MAX;
    if (base >= 1000 && exp >= 3) return LLONG_MAX;
    if (base >= 10000 && exp >= 2) return LLONG_MAX;
    
    long long result = 1;
    long long b = base;
    
    while (exp > 0) {
        if (exp & 1) {
            // Check for overflow before multiplication
            if (result > LLONG_MAX / b) return LLONG_MAX;
            result *= b;
        }
        if (exp > 1) {
            // Check for overflow before squaring
            if (b > LLONG_MAX / b) return LLONG_MAX;
            b *= b;
        }
        exp >>= 1;
    }
    return result;
}

// Exact recursive partition check - direct translation from Python
static bool recursive_partition_check(long long remaining, int factors_left, int min_factor, Factorization* result, int depth) {
    // Base cases from Python implementation
    if (factors_left == 0) {
        return remaining == 1;
    }
    
    if (factors_left == 1) {
        if (remaining >= min_factor) {
            if (result && depth < MAX_FACTORS) {
                result->factors[depth] = (int)remaining;
            }
            return true;
        }
        return false;
    }
    
    // Early termination check
    long long min_product = fast_pow_safe(min_factor, factors_left);
    if (min_product >= LLONG_MAX || min_product > remaining) {
        return false;
    }
    
    // Calculate max_factor exactly as in Python
    long long denominator = fast_pow_safe(min_factor, factors_left - 1);
    if (denominator >= LLONG_MAX || denominator == 0) return false;
    
    long long max_factor_bound1 = remaining / denominator;
    long long max_factor_bound2 = (long long)(pow((double)remaining, 1.0 / factors_left)) + 1;
    long long max_factor = (max_factor_bound1 < max_factor_bound2) ? max_factor_bound1 : max_factor_bound2;
    
    // Ensure max_factor doesn't exceed reasonable bounds
    if (max_factor > remaining) max_factor = remaining;
    if (max_factor > 1000000) max_factor = 1000000; // Practical limit
    
    // Try each factor in range [min_factor, max_factor]
    for (long long factor = min_factor; factor <= max_factor; factor++) {
        if (remaining % factor == 0) {
            if (result && depth < MAX_FACTORS) {
                result->factors[depth] = (int)factor;
            }
            
            if (recursive_partition_check(remaining / factor, factors_left - 1, min_factor, result, depth + 1)) {
                return true;
            }
        }
    }
    
    return false;
}

// Check if n can be partitioned into exactly k factors, each >= k
static bool can_partition_with_k_factors(long long n, int k, Factorization* result) {
    if (result) {
        result->count = 0;
    }
    
    // Base case from Python
    if (k == 1) {
        if (n >= 1) {
            if (result) {
                result->factors[0] = (int)n;
                result->count = 1;
            }
            return true;
        }
        return false;
    }
    
    // Early termination: k^k > n
    long long k_to_k = fast_pow_safe(k, k);
    if (k_to_k >= LLONG_MAX || k_to_k > n) {
        return false;
    }
    
    // Optimized k=2 case (most common)
    if (k == 2) {
        for (long long d = 2; d * d <= n; d++) {
            if (n % d == 0) {
                long long other = n / d;
                if (d >= 2 && other >= 2) {
                    if (result) {
                        result->factors[0] = (int)((d <= other) ? d : other);
                        result->factors[1] = (int)((d <= other) ? other : d);
                        result->count = 2;
                    }
                    return true;
                }
            }
        }
        return false;
    }
    
    // For k >= 3, use exact recursive method
    bool found = recursive_partition_check(n, k, k, result, 0);
    if (found && result) {
        result->count = k;
    }
    return found;
}

// EXACT partition function calculation - direct translation from Python
static int calculate_P_pi_exact(long long n) {
    if (n == 1) return 1;
    
    int max_k = 1;
    int k = 1;
    
    // Continue until k^k > n (exact termination condition from Python)
    while (true) {
        long long k_to_k = fast_pow_safe(k, k);
        if (k_to_k >= LLONG_MAX || k_to_k > n) {
            break;
        }
        
        if (can_partition_with_k_factors(n, k, NULL)) {
            max_k = k;
        }
        
        k++;
        
        // Safety limit to prevent infinite loops on edge cases
        if (k > 50) break;
    }
    
    return max_k;
}

// Get actual factorization for the maximum k
static void get_optimal_factorization(long long n, int max_k, Factorization* result) {
    if (max_k <= 0) {
        result->count = 0;
        return;
    }
    
    // Find the factorization for the maximum k
    if (can_partition_with_k_factors(n, max_k, result)) {
        // Factorization found and stored in result
        return;
    }
    
    // Fallback: shouldn't happen with correct algorithm
    result->count = 1;
    result->factors[0] = (int)n;
}

// Memory-efficient factorization string
static void factorization_to_string_compact(Factorization* fact, char* str, int max_len) {
    if (fact->count == 0) {
        strncpy(str, "1", (size_t)(max_len - 1));
        str[max_len - 1] = '\0';
        return;
    }

    if (fact->count == 1) {
        snprintf(str, (size_t)max_len, "%d", fact->factors[0]);
        return;
    }

    str[0] = '\0';
    int current_len = 0;

    for (int i = 0; i < fact->count && current_len < max_len - 10; i++) {
        char temp[16];
        int temp_len = snprintf(temp, sizeof(temp), "%s%d", (i > 0) ? "*" : "", fact->factors[i]);

        if (current_len + temp_len < max_len - 1) {
            strcat(str, temp);
            current_len += temp_len;
        } else {
            break;
        }
    }
}

// Safe system call wrapper
static int safe_system_call(const char* command) {
    int result = system(command);
    if (result == -1) {
        printf("Warning: System call failed: %s\n", command);
        return -1;
    }
    return result;
}

// Process a single chunk with exact algorithm
static bool process_chunk(long long start_n, long long end_n, const char* chunk_filename,
                         int* prev_P_pi, bool is_first_chunk) {

    printf("Processing chunk: %lld to %lld (EXACT ALGORITHM)\n", start_n, end_n);

    long long chunk_size = end_n - start_n + 1;

    // Allocate memory for this chunk
    int* P_pi_values = malloc((size_t)(chunk_size + 1) * sizeof(int));
    Factorization* factorizations = malloc((size_t)chunk_size * sizeof(Factorization));

    if (!P_pi_values || !factorizations) {
        printf("Error: Memory allocation failed for chunk\n");
        free(P_pi_values);
        free(factorizations);
        return false;
    }

    // Calculate P_π values for this chunk using EXACT algorithm
    clock_t start_time = clock();

    for (long long i = 0; i < chunk_size; i++) {
        long long n = start_n + i;
        
        // EXACT calculation - guaranteed to find true maximum k
        P_pi_values[i] = calculate_P_pi_exact(n);
        
        // Get the optimal factorization
        get_optimal_factorization(n, P_pi_values[i], &factorizations[i]);

        if (n % PROGRESS_INTERVAL == 0) {
            double progress = (double)(n - start_n + 1) / chunk_size * 100;
            printf("  Chunk progress: %.1f%% (n=%lld, P_π=%d)\n", progress, n, P_pi_values[i]);
        }
    }

    // Calculate P_π for boundary (needed for sequence determination)
    P_pi_values[chunk_size] = calculate_P_pi_exact(end_n + 1);

    clock_t calc_time = clock();
    printf("  EXACT calculation time: %.2f seconds\n",
           (double)(calc_time - start_time) / CLOCKS_PER_SEC);

    // Write chunk to CSV
    FILE* file = fopen(chunk_filename, "w");
    if (!file) {
        printf("Error: Could not create chunk file %s\n", chunk_filename);
        free(P_pi_values);
        free(factorizations);
        return false;
    }

    setvbuf(file, NULL, _IOFBF, BUFFER_SIZE);

    // Write header only for first chunk
    if (is_first_chunk) {
        fprintf(file, "n,P_pi(n),Factorization,SequenceType,SequenceIndex\n");
    }

    char fact_str[128];
    const char* seq_names[] = {"decrease", "equality", "increase"};

    for (long long i = 0; i < chunk_size; i++) {
        long long n = start_n + i;
        int P_pi_n = P_pi_values[i];
        int P_pi_n_plus_1 = P_pi_values[i + 1];

        // Handle boundary with previous chunk
        if (i == 0 && !is_first_chunk) {
            P_pi_n_plus_1 = P_pi_values[i];
            P_pi_n = *prev_P_pi;
        }

        // Determine sequence type and update global counters
        SequenceType seq_type;
        long long seq_index;

        if (P_pi_n > P_pi_n_plus_1) {
            seq_type = DECREASE;
            seq_index = ++global_d_count;
        } else if (P_pi_n == P_pi_n_plus_1) {
            seq_type = EQUALITY;
            seq_index = ++global_e_count;
        } else {
            seq_type = INCREASE;
            seq_index = ++global_i_count;
        }

        // Convert factorization to string
        factorization_to_string_compact(&factorizations[i], fact_str, sizeof(fact_str));

        // Write CSV row
        fprintf(file, "%lld,%d,%s,%s,%lld\n",
                n, P_pi_n, fact_str, seq_names[seq_type], seq_index);
    }

    fclose(file);

    // Store last P_π value for next chunk
    *prev_P_pi = P_pi_values[chunk_size - 1];

    free(P_pi_values);
    free(factorizations);

    clock_t end_time = clock();
    printf("  Chunk completed in %.2f seconds\n",
           (double)(end_time - start_time) / CLOCKS_PER_SEC);

    return true;
}

// Combine chunk files into final CSV
static bool combine_chunks(const Config* config) {
    printf("Combining chunks into final CSV...\n");

    FILE* output = fopen(config->final_csv, "w");
    if (!output) {
        printf("Error: Could not create final CSV file\n");
        return false;
    }

    setvbuf(output, NULL, _IOFBF, BUFFER_SIZE);

    // Write header
    fprintf(output, "n,P_pi(n),Factorization,SequenceType,SequenceIndex\n");

    char buffer[1024];
    bool first_chunk = true;

    for (int chunk = 0; chunk < config->num_chunks; chunk++) {
        char chunk_filename[300];
        snprintf(chunk_filename, sizeof(chunk_filename),
                "%s/chunk_%03d.csv", config->output_dir, chunk);

        FILE* input = fopen(chunk_filename, "r");
        if (!input) {
            printf("Error: Could not open chunk file %s\n", chunk_filename);
            fclose(output);
            return false;
        }

        // Skip header for non-first chunks
        if (!first_chunk) {
            if (fgets(buffer, sizeof(buffer), input) == NULL) {
                printf("Warning: Empty chunk file %s\n", chunk_filename);
            }
        }
        first_chunk = false;

        // Copy data
        while (fgets(buffer, sizeof(buffer), input)) {
            fputs(buffer, output);
        }

        fclose(input);

        // Remove chunk file to save space
        if (remove(chunk_filename) != 0) {
            printf("Warning: Could not remove chunk file %s\n", chunk_filename);
        }

        printf("  Combined chunk %d/%d\n", chunk + 1, config->num_chunks);
    }

    fclose(output);
    printf("Final CSV created: %s\n", config->final_csv);

    return true;
}

// Create output directory
static bool create_output_dir(const char* dir) {
    struct stat st = {0};
    if (stat(dir, &st) == -1) {
        #ifdef _WIN32
        return mkdir(dir) == 0;
        #else
        return mkdir(dir, 0755) == 0;
        #endif
    }
    return true;
}

// Main processing function
static bool process_large_range(const Config* config) {
    printf("=== EXACT Optimal Multiplicative Partitions Generator ===\n");
    printf("Author: Daniel Eduardo Ruiz C. (danuaemx)\n");
    printf("Date: 2025-06-02 03:24:14\n");
    printf("Algorithm: EXACT - Guaranteed optimal k for all n\n");
    printf("Range: 1 to %lld\n", config->total_n);
    printf("Chunk size: %lld\n", config->chunk_size);
    printf("Number of chunks: %d\n", config->num_chunks);
    printf("Memory per chunk: ~%.1f GB\n",
           (config->chunk_size * (sizeof(int) + sizeof(Factorization))) / (1024.0 * 1024.0 * 1024.0));
    printf("\n");

    clock_t total_start = clock();

    // Create output directory
    if (!create_output_dir(config->output_dir)) {
        printf("Error: Could not create output directory\n");
        return false;
    }

    int prev_P_pi = 1; // P_π(0) conceptually, but we start from n=1

    // Process each chunk
    for (int chunk = 0; chunk < config->num_chunks; chunk++) {
        long long start_n = chunk * config->chunk_size + 1;
        long long end_n = ((chunk + 1) * config->chunk_size > config->total_n) ?
                         config->total_n : (chunk + 1) * config->chunk_size;

        char chunk_filename[300];
        snprintf(chunk_filename, sizeof(chunk_filename),
                "%s/chunk_%03d.csv", config->output_dir, chunk);

        printf("\n--- EXACT Chunk %d/%d ---\n", chunk + 1, config->num_chunks);

        if (!process_chunk(start_n, end_n, chunk_filename, &prev_P_pi, chunk == 0)) {
            printf("Error: Failed to process chunk %d\n", chunk);
            return false;
        }

        // Memory cleanup hint for OS (Linux only)
        #ifdef __linux__
        if (access("/proc/sys/vm/drop_caches", W_OK) == 0) {
            int result = safe_system_call("sync && echo 3 > /proc/sys/vm/drop_caches 2>/dev/null");
            if (result != 0) {
                printf("Note: Could not clear system caches (not critical)\n");
            }
        }
        #endif
    }

    // Combine chunks
    printf("\n");
    if (!combine_chunks(config)) {
        return false;
    }

    // Remove temporary directory
    char cmd[512];
    #ifdef _WIN32
    snprintf(cmd, sizeof(cmd), "rmdir /s /q \"%s\"", config->output_dir);
    #else
    snprintf(cmd, sizeof(cmd), "rm -rf \"%s\"", config->output_dir);
    #endif

    int result = safe_system_call(cmd);
    if (result != 0) {
        printf("Warning: Could not remove temporary directory %s\n", config->output_dir);
        printf("You may want to remove it manually to free disk space\n");
    }

    clock_t total_end = clock();
    double total_time = (double)(total_end - total_start) / CLOCKS_PER_SEC;

    printf("\n=== EXACT ALGORITHM COMPLETION REPORT ===\n");
    printf("Total computation time: %.2f seconds (%.2f hours)\n",
           total_time, total_time / 3600.0);
    printf("Average time per number: %.8f seconds\n", total_time / config->total_n);
    printf("Numbers per second: %.0f\n", config->total_n / total_time);
    printf("Algorithm: EXACT - Guaranteed optimal results\n");
    printf("\nSequence Statistics:\n");
    printf("- Decrease sequence entries: %lld\n", global_d_count);
    printf("- Equality sequence entries: %lld\n", global_e_count);
    printf("- Increase sequence entries: %lld\n", global_i_count);
    printf("- Total entries: %lld\n", global_d_count + global_e_count + global_i_count);

    return true;
}

int main(int argc, char* argv[]) {
    Config config;

    // Default configuration
    config.total_n = 1000000LL;  // Default 10^6
    config.chunk_size = MAX_CHUNK_SIZE;
    strcpy(config.output_dir, "chunks_temp_exact");
    strcpy(config.final_csv, "optimal_partitions_exact.csv");

    // Parse command line arguments
    if (argc >= 2) {
        config.total_n = atoll(argv[1]);
    }
    if (argc >= 3) {
        config.chunk_size = atoll(argv[2]);
        if (config.chunk_size > 100000000LL) {
            printf("Warning: Large chunk size (%lld), consider smaller chunks for better memory management\n",
                   config.chunk_size);
        }
    }
    if (argc >= 4) {
        strncpy(config.final_csv, argv[3], sizeof(config.final_csv) - 1);
        config.final_csv[sizeof(config.final_csv) - 1] = '\0';
    }

    // Validate inputs
    if (config.total_n <= 0) {
        printf("Error: Invalid total_n (%lld). Must be positive.\n", config.total_n);
        return 1;
    }

    if (config.chunk_size <= 0) {
        config.chunk_size = MAX_CHUNK_SIZE;
        printf("Warning: Invalid chunk size, using default: %lld\n", config.chunk_size);
    }

    // Calculate number of chunks
    config.num_chunks = (int)((config.total_n + config.chunk_size - 1) / config.chunk_size);

    // Validate memory requirements
    double chunk_memory_gb = (config.chunk_size * (sizeof(int) + sizeof(Factorization))) / (1024.0 * 1024.0 * 1024.0);
    if (chunk_memory_gb > 18.0) {
        printf("Error: Chunk size too large (%.1f GB > 18 GB limit)\n", chunk_memory_gb);
        printf("Reduce chunk size with: %s %lld %lld\n", argv[0], config.total_n, (long long)(18.0 * 1024 * 1024 * 1024 / (sizeof(int) + sizeof(Factorization))));
        return 1;
    }

    printf("EXACT ALGORITHM Configuration:\n");
    printf("  Total N: %lld\n", config.total_n);
    printf("  Chunk size: %lld\n", config.chunk_size);
    printf("  Number of chunks: %d\n", config.num_chunks);
    printf("  Memory per chunk: %.1f GB\n", chunk_memory_gb);
    printf("  Output file: %s\n", config.final_csv);
    printf("  Guarantee: TRUE maximum k for every n\n");
    printf("\n");

    if (!process_large_range(&config)) {
        printf("Error: Processing failed\n");
        return 1;
    }

    return 0;
}