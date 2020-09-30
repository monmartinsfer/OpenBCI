# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759306 
"""

import numpy as np
#from scipy import signal
from neurodsp import spectral
from lspopt.lsp import spectrogram_lspopt

class spectrum():

    # Inicializar espectro
    def __init__(self, constants):      #Recibe las constantes DESDE Data_Manager
        self.constants = constants

    # Obtiene la distribución de potencias de la señal recibida en el dominio de las frecuencias
    def get_spectrum(self, samples):    #Recibe DESDE Data_Manager las muestras tomadas y guardadas en el BUFFER tras ser filtradas

        spectrums = []
        # Trata la señal almacenada en cada fila de la muestra, proveniente de cada sensor
        for i in range(self.constants.NDIMS):
            # Calcula la frecuencia y el espectro de potencia de la muestra y la añade al vector de espectros
            freqs, spectre = spectral.compute_spectrum(samples[i,:], self.constants.SAMPLE_RATE) #Analiza las muestras a la frecuencia de muestreo
            spectrums.append(spectre)
        return freqs, np.asarray(spectrums)     #Devuelve la frecuencia y una matriz de espectros

    # Obtiene el espectrograma de las muestras
    def get_spectrogram(self, samples):     #Recibe DESDE Data_Manager las muestras tomadas y guardadas en el BUFFER tras ser filtradas
        # _, _, Sxx = signal.spectrogram(samples, self.constants.SAMPLE_RATE)
        # Crear un espectrograma --> Mejora la calidad del espectrograma aplicando una ventana del parámtro especificado
        _, _, Sxx = spectrogram_lspopt(samples, self.constants.SAMPLE_RATE, c_parameter=20.0)
        return Sxx