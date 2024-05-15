# Efectos de Audio

En esta sección se va a explicar cada efecto implementado

## Eco Simple

La implentación del eco fue la siguiente

<p align="center">
  <img src="img/Eco_simple.png" alt="Eco simple diagrama en bloques" width="500">
</p>

En donde la función transferencia es $$H(z) = \frac{z^{-\tau}}{1-gz^{-\tau}}$$ al expresar esto como una ecuación en diferencias obtenemos 
$$y(n) = x(n-\tau) + y(n-\tau)g$$
en donde $\tau$ es el tiempo de dealy, este es del tamaño de la señal, y $g$ es la ganancia del lazo de realimentación, este valor debe ser $0<g<1$ para que el lazo sea estable. La impletentación en el codigo permite seleccionar la cantidad de repeticiones del eco, expresado en veces. De forma tal que la respuesta al escalón esta dada 

<p align="center">
  <img src="img/respuesta al escalon.png" alt="Respuesta al escalón eco simple" width="400">
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
  <img src="img/flanger.png" alt="Flanger diagrama en bloques" width="400">
</p>

Esta es su ecuación en diferencias

$$y(n) = x(n) + x(n-M(n))g$$

donde $M(n)$ es una senal discreta y periodica, modelada con un **LFO**, (Low Frecuency Oscilator). El tiempo de delay va desde 0 $ms$ a 15 $ms$. El usuario puede cambiar la duración del delay, la frecuencia del **LFO**, la tensión DC de base y la ganancia de este delay.

## Chorus

La implementación es similar a la del Flanger, teniendo un diagrama en bloques parecido.

<p align="center">
  <img src="img/Blank diagram.png" alt="Chorus diagrama en bloques" width="500">
</p>

Es la implementación en paralelo de 4 chorus, donde el delay de cada uno va entre 10 $ms$ y 25 $ms$. La razón por la que se implementan 4 en paralelo es para mejorar el efecto. Su función transferencia es de la siguiente manera

$$y(n) = x(n)g + x(n-M_1(n))g_1 + x(n-M_2(n))g_2 + x(n-M_3(n))g_3 + x(n-M_4(n))g_4$$

Donde $M_n$ es el delay de cada etapa y $g_n$ su respectiva ganancia y $g$ la ganancia del sonido original.