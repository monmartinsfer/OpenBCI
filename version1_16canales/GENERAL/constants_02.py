# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759306 
"""

import sys  #Path
import os   #Path


class constants():

    # Inicializa las constantes
    def __init__(self, seconds=6, sample_rate=250, baud=115200, channels=8, ndims=8, signal='eeg', lowcut=1, highcut=45, order=5):

        # Definición de Constantes
        self.ADDRESS = '192.168.1.104'                                              # DIRECCIÓN IP
        #self.ADDRESS = '10.1.25.82'
        self.PORT = 10000                                                           # PUERTO
        self.SECONDS = seconds                                                      # Segundos
        self.SAMPLE_RATE = sample_rate                                              # Frecuencia de Muestreo
        self.NOTCH = 50                                                             # Frecuencia del filtro Notch
        self.BAUD = baud                                                            # Baudios (comunicación Serial)
        self.WINDOW = self.SAMPLE_RATE * self.SECONDS                               # Ventana de muestreo = 250 * 6 = 1500 muestras
        self.LARGE_WINDOW = self.SAMPLE_RATE * 60                                   # 1 minuto de visualización
        self.CHANNELS = channels                                                    # NÚMERO CANALES / SENSORES
        self.NDIMS = ndims
        self.SIGNAL = signal                                                        # Señal 'eeg' = electrocardiograma
        self.LOWCUT = lowcut                                                        # Limite inferior del rango de frecuencias
        self.HIGHCUT = highcut                                                      # Limite superior del rango de frecuencias
        self.ORDER = order                                                          # Orden del Filtro Butterworth
        self.METHOD = 'Butterworth'                                                 # Método Filtrado
        self.FILTER_RANGES = [[1,4],[4,8],[8,16],[16,32],[32,45]]                   # Rangos de frecuencias
        self.CHANNEL_IDS = ['F1', 'F2', 'C3', 'C4', 'P7', 'P8', 'O1', 'O2']          # Nombres de los canales (8 sensores)
        self.AVAILABLE_CHANNELS = [True,True,True,True,True,True,True,True]         # Disponibilidad de Canales
        self.PATH = sys.path.append(os.path.realpath('./RESULTS/'))                 # añadir un Path para los resultados

        # dinamic variables
        self.last_action = 5                                                        # Última acción solicitada
        self.pos_ini = self.LARGE_WINDOW - self.WINDOW                              # Posición inicial del rango de puntos para una muestra pequeña
        self.pos_end = self.LARGE_WINDOW                                            # Posición final del rango de puntos para una muestra pequeña
        self.running_trial = 0                                                      # Conjunto de medidas actual
        self.running_window = 0                                                     # Ventana de muestreo actual
        self.ispath = False                                                         # Indicador para acceso al archivo EDF
        self.refresh_rate = 1/sample_rate                                           # Frecuencia de actualización
        self.short_refresh_rate = 1/sample_rate                                     # Frecuencia corta de actualización

    # Actualización de los datos
    def update(self, name, value):
        # Actualización de los segudnos
        if name == 'seconds':
            self.SECONDS = value   
            self.WINDOW = self.SAMPLE_RATE * self.SECONDS
            self.pos_ini = self.LARGE_WINDOW - self.WINDOW - self.SAMPLE_RATE/2
            self.pos_end = self.LARGE_WINDOW - self.SAMPLE_RATE/2
        # Actualización del orden
        elif name == 'order':
            self.ORDER = value
        # Actualización del método
        elif name == 'method':
            self.METHOD = value
            if value != 'Butterworth':
                self.short_refresh_rate = 0.05           # Frecuencia FIJA de actualización de plots de 50ms
            else:
                self.short_refresh_rate = self.refresh_rate

    # Selección del Rango de Frecuencias
    def set_filter_range(self, activated):
        # Todos los rangos de frecuencias: 1 - 45
        if activated == 'Full':
            self.LOWCUT, self.HIGHCUT = 1, 45
        # Rango DELTA = 1 - 4
        elif activated == 'Delta':
            self.LOWCUT, self.HIGHCUT = self.FILTER_RANGES[0]
        # Rango THETA = 4 - 8
        elif activated == 'Theta':
            self.LOWCUT, self.HIGHCUT = self.FILTER_RANGES[1]   
        # Rango ALPHA = 8 - 16
        elif activated == 'Alpha':
            self.LOWCUT, self.HIGHCUT = self.FILTER_RANGES[2]    
        # Rango BETA = 16 - 32
        elif activated == 'Beta':
            self.LOWCUT, self.HIGHCUT = self.FILTER_RANGES[3]   
        # Rango GAMMA = 32 - 45
        elif activated == 'Gamma':
            self.LOWCUT, self.HIGHCUT = self.FILTER_RANGES[4]    
          
        
