// Cooley-Tukey radix-2 FFT
#include <complex.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#ifndef N
    #define N 4096
#endif

void fft(complex float* in, complex float* out, size_t n);

int main() {
    // Generate a signal
    size_t n = N;
    complex float* in = malloc(n * sizeof(complex float));
    for(size_t i = 0; i < n; i++){
        in[i] = sin(40 * 2 * M_PI * i/n) + 0.5 * sin(90 * 2 * M_PI * i/n);
    }

    // Write input to a file
    FILE* in_file = fopen("fft_input.txt", "w");
    for(size_t i = 0; i < n; i++){
        fprintf(in_file, "%f\n", crealf(in[i]), cimagf(in[i]));
    }
    fclose(in_file);

    // Compute FFT
    complex float* out = malloc(n * sizeof(complex float));
    fft(in, out, n);

    // Write output to a file
    FILE* out_file = fopen("fft_output.txt", "w");
    for(size_t i = 0; i < n; i++){
        fprintf(out_file, "%f+%fj\n", crealf(out[i]), cimagf(out[i]));
    }
    fclose(out_file);

    // Free allocated memory
    free(in);
    free(out);

    return 0;
}

// RADIX-2 Cooley-Tukey FFT
/*
    in: pointer to the input array of complex numbers. this is the discrete time signal
    out: pointer to the output array of complex numbers. this is the frequency domain representation
    n: number of samples in the input signal
*/
void fft(complex float* in, complex float* out, size_t n){
    if(n == 1){
        out[0] = in[0];
        return;
    }

    // Split into the DIT FFTs
    complex float* even = malloc(n/2 * sizeof(complex float));
    complex float* odd = malloc(n/2 * sizeof(complex float));

    for(size_t i = 0; i < n/2; i++){
        even[i] = in[2*i];
        odd[i] = in[2*i+1];
    }

    complex float* even_out = malloc(n/2 * sizeof(complex float));
    complex float* odd_out = malloc(n/2 * sizeof(complex float));

    fft(even, even_out, n/2);
    fft(odd, odd_out, n/2);
    
    // Join the results and apply twiddle factors
    for(size_t i = 0; i < n/2; i++){
        // Compute twiddle
        complex float twiddle = cexp(-2 * M_PI * I * i / n) * odd_out[i];
        // Butterfly operation: X[k] = E[k] + W_N^k * O[k]
        out[i] = even_out[i] + twiddle;
        out[i + n/2] = even_out[i] - twiddle;
    }
    
    free(even);
    free(odd);
    free(even_out);
    free(odd_out);
}