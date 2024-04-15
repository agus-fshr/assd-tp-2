// Cooley-Tukey radix-2 FFT
#include <complex.h>
#include <math.h>
#include <stdio.h>

int main() {
    // Generate a signal
    size_t n = 500;
    complex float* in = malloc(n * sizeof(complex float));
    for(size_t i = 0; i < n; i++){
        in[i] = sin(40 * 2 * M_PI * i/n) + 0.5 * sin(90 * 2 * M_PI * i/n);
    }

    // Compute FFT
    complex float* out = malloc(n * sizeof(complex float));
    fft(in, out, n);

    // Write output to a file
    FILE* file = fopen("fft_output.txt", "w");
    for(size_t i = 0; i < n; i++){
        fprintf(file, "%f + %fi\n", crealf(out[i]), cimagf(out[i]));
    }
    fclose(file);

    // Free allocated memory
    free(in);
    free(out);

    return 0;
}

// RADIX-2 Cooley-Tukey FFT
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
    
    for(size_t i = 0; i < n/2; i++){
        complex float twiddle = cexp(-2 * M_PI * I * i / n) * odd_out[i];
        out[i] = even_out[i] + twiddle;
        out[i + n/2] = even_out[i] - twiddle;
    }
    
    free(even);
    free(odd);
    free(even_out);
    free(odd_out);
}