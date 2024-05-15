# ASSD TP #2
Grupo #5 | Integrantes:
- Casas, Agustín
- Dalzotto, Rafael
- Fisher, Agustín
- Oms, Mariano Alejandro

# FFT
### Implementacion en C
Para la implementacion en C del algoritmo de la FFT se eligio usar el algoritmo de Cooley-Tukey con Decimation-in-Time (DIT). La implementacion en sencilla.

```C
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
```

### Comparacion con numpy.fft.fft()
A traves de un breve script en Python se compila y ejecuta el codigo de C, editando el numero de muestras y tomando todos los puntos de la entrada y salida del codigo de C. Usando `numpy.fft.fft()`.

```Python
import numpy as np
import matplotlib.pyplot as plt
import os

# Set number of samples
N = 512

# Compile and run the C program
os.system(f'cd FFT && make clean && make N={N} && ./main')

# Read in FFT values from the C program
fft_c = np.loadtxt('FFT/fft_output.txt', dtype=complex)

# Fetch the input sine wave from the C program
sine = np.loadtxt('FFT/fft_input.txt')
fft_py = np.fft.fft(sine)

# Plot both FFTs
plt.plot(np.abs(fft_py), label='Python')
plt.plot(np.abs(fft_c), label='C')
plt.legend()
plt.show()
```

Para una entrada con la forma $\sin(80\pi t/N) + 0.5\sin(180\pi t/N)$ y `N = 128` el programa arroja el siguiente grafico.
<p align="center">
  <img src="informe/img/FFT_Python_C_128.png" alt="FFT en Python vs. C para N=128" width="500">
</p>

Es interesante ver lo que pasa si `N` toma un valor que no es potencia de 2.

<p align="center">
  <img src="informe/img/FFT_Python_C_500.png" alt="FFT en Python vs. C para N=128" width="500">
</p>

Se ve que el resultado no esta alejado del correcto. Sin embargo se pierde mucha resolucion. Hay picos donde deberian estar pero el espectro esta contaminado y los picos no llegan a tener la amplitud que deberian tener.

# Sintesis por Modelado Fisico con Karplus-Strong
En este trabajo se utilizo modelado fisico para sintesis de cuerdas de Karplus-Strong para sintetizar el sonido de una guitarra acustica.

<p align="center">
  <img src="informe/img/KS_Block_Diagram.png" alt="FFT en Python vs. C para N=128" width="500">
</p>

Este es el diagrama de bloques basico propuesto por Karplus y Strong.

El algoritmo funciona tomando, primero, una muestra de ruido. Este ruido puede tener diferentes distrubuciones, esto se analizara mas adelante. Luego esa secuencia inicial de ruido pasa por una linea de retardo de longitud $L$, que es la longitud del arreglo. Esto simula la longitud de la cuerda de la guitarra. Esta senal es realimentada a traves de un filtro que tiene la siguiente forma
$$y(t) = 0.5(y(t-L) + y(t-L-1))$$

Esto suaviza la senal y permite que los armonicos mas altos decaigan rapidamente, como en una cuerda real.

La frecuencia de la nota generada tiene la siguiete expresion 
$$f = \frac{f_s}{L+\frac{1}{2}}$$

El sistema tiene transferencia
$$H(z) = \frac{ 1 + z^{-1} }{2 - R_Lz^{-L} - R_L z^{-(L+1)}}$$

# Efectos de Audio

En esta sección se va a explicar cada efecto implementado

## Eco Simple

La implentación del eco fue la siguiente

<p align="center">
  <img src="informe/img/Eco_simple.png" alt="Eco simple diagrama en bloques" width="500">
</p>

En donde la función transferencia es $$H(z) = \frac{z^{-\tau}}{1-gz^{-\tau}}$$ al expresar esto como una ecuación en diferencias obtenemos 
$$y(n) = x(n-\tau) + y(n-\tau)g$$
en donde $\tau$ es el tiempo de dealy, este es del tamaño de la señal, y $g$ es la ganancia del lazo de realimentación, este valor debe ser $0 < g < 1$ para que el lazo sea estable. La impletentación en el codigo permite seleccionar la cantidad de repeticiones del eco, expresado en veces. De forma tal que la respuesta al escalón esta dada 

<p align="center">
  <img src="informe/img/respuesta al escalon.png" alt="Respuesta al escalón eco simple" width="400">
</p>

donde la respuesta al escalon esta dada de la siguiente forma
$$h(n) = \delta(t - \tau) + g\delta(t - 2\tau) + g^2\delta(t - 3\tau) + ... $$

donde esta repetción se da las veces preestablecidas por el usuario.

## Reverberador plano

La implemtentacón de este es similar a la del eco simple, siendo el diagramas de bolques y la función transferencia iguales al caso anterior, la unica diferencia es que el usuario puede selecciónar el tiempo de delay en el cual arranquen las reverberaciones. 

## Reververador por convolución

Este efecto se basa en convolucionar el sonido de entrada con la respuesta al escalón de una habitación, también llamados **RIR**. Al hacer esto se puede simular el sonido en esa habitación.

$$y(n) = (x*h)(n) $$

donde $h(n)$ es una RIR.

## Flanger

La implentación esta basada en el siguiente esquema

<p align="center">
  <img src="informe/img/flanger.png" alt="Flanger diagrama en bloques" width="400">
</p>

Esta es su ecuación en diferencias

$$y(n) = x(n) + x(n-M(n))g$$

donde $M(n)$ es una senal discreta y periodica, modelada con un **LFO**, (Low Frecuency Oscilator) y $g$ la ganancia. El tiempo de delay va desde 0 $ms$ a 15 $ms$. El usuario puede cambiar la duración del delay, la frecuencia del **LFO**, la tensión DC de base y la ganancia de este delay.

## Chorus

La implementación es similar a la del Flanger, teniendo un diagrama en bloques parecido.

<p align="center">
  <img src="informe/img/Blank diagram.png" alt="Chorus diagrama en bloques" width="500">
</p>

Es la implementación en paralelo de 4 chorus, donde el delay de cada uno va entre 10 $ms$ y 25 $ms$. La razón por la que se implementan 4 en paralelo es para mejorar el efecto. Su función transferencia es de la siguiente manera

$$y(n) = x(n)g + x(n-M_1(n))g_1 + x(n-M_2(n))g_2 + x(n-M_3(n))g_3 + x(n-M_4(n))g_4$$

Donde $M_n$ es el delay de cada etapa y $g_n$ su respectiva ganancia y $g$ la ganancia del sonido original.
