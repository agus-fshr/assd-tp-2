import numpy as np

def process_mix(mix_vector, Nsample):
    f0 =1
    flast = f0
    Nsample = int(Nsample)
    Msample = int(Nsample/2)                 #El segundo array (auxiliar)
    scaled_mix = []
    for SegmentIndex in range(0, len(mix_vector), Nsample):             # proceso por partes el vector
        mix_segment = mix_vector[SegmentIndex : SegmentIndex + Nsample +Msample]    # este incluye el arreglo auxiliar, va de mix[SegmentIndex]
        scaled_mix_Segment, flast = fsm(mix_segment, Nsample, Msample, flast)       #Calculo el segmento escalado
        scaled_mix.extend(scaled_mix_Segment)                                       #Se lo agrego al vector
    return scaled_mix




def fsm(subVectorNM, Nsample, Msample, f0, printFlag = False):
    if printFlag:
        print(f'Entro a la fsm con subVec = {subVectorNM}, Ns = {Nsample}, Ms = {Msample}')
    segmentN = subVectorNM[0 : Nsample]
    segmentM = subVectorNM[Nsample : Nsample+Msample]


    X1index = np.argmax(np.abs(segmentN)) #Encuentro X1 (maximo del primer array)
    X1 = np.abs(segmentN[X1index])
    if len(segmentM) == 0:
        segmentM = [0.005]                     #Lo pongo como que tiene un elemento muy chico
        X2 = 0.005
    else:
        X2index = np.argmax(np.abs(segmentM)) #Encuentro X2 (maximo del segundo array)
        X2 = np.abs(segmentM[X2index])

    scaledSegmentN = segmentN #Por defecto le asigno el original (debugging purposes)
    ffinal = 1                #Factor de escala final (en nr1) lo defino por defecto como 1 (debugging purposes)

    if (X1>1):      #Si X1>1 ejecuto el algoritmo para escalar
        f1 = 1/X1
        nl1, nr1 = find_nr_nl(segmentN)     
        if(X2==0):
            f2 = 1.05       #Se rompe todo sino
        else:
            f2 = 1/X2       #Despues veo si hace falta escalar en el segundo cuando saco las pendientes

        nl2, nr2 = find_nr_nl(segmentM)
        nl2 = nl2+Nsample
        nr2 = nr2 + Nsample                 #Los dejo en relacion al 0 del arreglo, que es el 0 del vector segmentN
        #Ahora calculo las pendientes
        SR1 = calculateSR1(f0,f1,f2,nl1,nl2,Nsample)
        fnl1 = calculate_f_of_n(f0, SR1, nl1)
        SR2 = calculateSR2(f1, f2, fnl1, nl1, nr1, nl2)
        fnr1 = calculate_f_of_n(fnl1, SR2, nr1)
        fnr2 = calculate_f_of_n(fnl1, SR2, nr2)
        SR3 = calculateSR3(f2,fnr1, fnr2, nr1, nl2, Nsample)
        #con las pendientes escalo el vector
        scaledSegmentN, ffinal = ScaleVector(segmentN, SR1, SR2, SR3, nl1, nr1, f0, fnl1, fnr1)


    else:
        if(X2>1):
            f2 = 1/X2 
            nl2, nr2 = find_nr_nl(segmentM)
            nl2 = nl2+Nsample
            nr2 = nr2 + Nsample
            SE = (f2-f0)/nl2
            scaledSegmentN, ffinal = ScaleVector_Single_Slope( segmentN, SE, f0)          #Pre-escalo asi no hay un salto tan brusco en el factor de escala
        else:
            SD = (1-f0)/(4*Nsample)
            scaledSegmentN,  ffinal = ScaleVector_Single_Slope( segmentN, SD, f0)          #Llevo de a poco el factor de escala a 1 nuevamente
    if printFlag:
        print(f'Devuelvo scaled = {scaledSegmentN}, ffinal = {ffinal}')
    return scaledSegmentN, ffinal     

#Para el caso de que X1<1 y X2>1
#Recibe solo una pendiente SE, la f0 y el vector de las primeras N muestras
def ScaleVector_Single_Slope ( segmentN, Slope, f0):  
    scaled_vector = []
    ffinal = 1
    for n, value in enumerate(segmentN):
        scaled_value = value * (f0 + n*Slope)
        scaled_vector.append(scaled_value)
        ffinal = (f0 + n*Slope)
    return scaled_vector, ffinal


    
def ScaleVector(segmentN, SR1, SR2, SR3, nl1, nr1, f0, fnl1, fnr1):
    scaled_vector = []
    ffinal = 1
    for n, value in enumerate(segmentN):
        if n < nl1:
            scaled_value = value * (f0 + n*SR1)
        elif nl1 <= n < nr1:
            scaled_value = value * (fnl1 + (n-nl1)*SR2)
        else:
            scaled_value = value * (fnr1 + (n-nr1)*SR3)
            ffinal = (fnr1 + (n-nr1)*SR3)
        scaled_vector.append(scaled_value)
    return scaled_vector, ffinal


#Encuentra la primera posicion del array en pasarse de 1 (nl) y la ultima en pasarse (nr)
def find_nr_nl(subVector):
    nl= [-1, 1]    #index, value
    nr= [-1, 1]   #index, value
    for i, value in enumerate(subVector):
            valabs = np.abs(value)
            if valabs > 1:
                if (nl[0] == -1):
                    nl[0] = i
                    nl[1] = valabs
                else:
                    nr[0] = i
                    nr[1] = valabs

    if (nr[0] == -1):   #Solo se pasa de 1 en una posicion
        nr[0] = nl[0]

    return nl[0], nr[0]
    
def calculate_f_of_n(f_ini,Slope, n):
    f_of_n = f_ini+Slope*n
    return f_of_n

#Calcula la pendiente para la recta del factor de escala en la region 1, entre n=1 y n=nl1
#f0: factor de escala inicial
#f1: factor de escala minimo para n in [1,N]
#f2: factor de escala minimo para n in [N+1,N+M]
#nl1: primer n tal que |X(n)| >= 1 para n in [1,N]
#nl2: primer n tal que |X(n)| >= 1 para n in [N+1,N+M]
def calculateSR1(f0, f1, f2, nl1, nl2, Nsample):
    #print(f'Entro con nl1 = {nl1}, nl2 = {nl2}')
    if nl1 == 0:
        S1 = (f1 -f0)          #si el indice es 0, no puedo dividir
    else:
        S1 = (f1 -f0)/nl1   #candidato 1

    #Ahora calculo el segundo candidato
    if f2 < 1:
        S2 = (f2- f0)/nl2
    else:
        S2 = (f2-f0)/(2*Nsample)

    SR1 =0
    if S1<S2:   #el caso mas critico es el que requiera la menor pendiente(mas negativa)
        SR1 = S1
    else:
        SR1 = S2
    return SR1

def calculateSR2(f1, f2, fnl1 ,nl1,nr1, nl2):
    S3=0
    S4=0
    if (nl1 != nr1):
        S3 = (f1 -fnl1)/(nr1- nl1)
    else:
        S3 =0
    

    if f2 < 1:
        S4 = (f2- fnl1)/(nl2-nl1)
    else:
        S4 = 0
    SR2 =0
    if S3<S4:
        SR2 = S3
    else:
        SR2 = S4
    return SR2

def calculateSR3(f2, fnr1, fnr2, nr1, nl2, Nsample):
    S5=0
    S6=0
    
    S5 = (f2 - fnr1)/(2*Nsample)    #primer candidato
    
    if f2 < 1:                      #segundo candidato
        S6 = (f2- fnr1)/(nl2-nr1)   #Si necesito que el factor sea menor a 1 en el punto de X2
    else:
        S6 = (1-fnr1)/(2*Nsample)   #si X2 no supera 1, trato de llevar el factor a 1

    
    SR3 =0
    if (f2>1) :     #Si no necesito escalar hacia abajo
        if S5<S6:
            SR3 = S5
        else:
            SR3 = S6

    elif (f2>fnr2):
        SR3 = S5
    else: 
        SR3 = S6
    return SR3




t = np.linspace(0, 13, 60000)

x = np.sin(2 * np.pi * t / 5)

envelope = -1*x*np.log10(t)*(1 - np.tanh(t-5)) + 0.5 + 2*np.exp(-50*(t-9)**2) +  np.exp(-200*(t-11)**2)
signal = np.sin(2 * np.pi * 20 * t) * envelope


newSignal2 = process_mix(signal, 500)

import matplotlib.pyplot as plt
ax1 = plt

ax1.plot(t, envelope, label='Original Envelope', color='blue')
ax1.axhline(y=1, color='black', linestyle='--', lw=1.5, label='Threshold')
ax1.plot(t, newSignal2, label='New Signal', color='green', lw=0.7)
ax1.grid()
ax1.legend()
plt.tight_layout()
plt.xlim(t[0], t[-1])
plt.show()