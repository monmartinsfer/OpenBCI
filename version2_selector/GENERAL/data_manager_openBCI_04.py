# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759306 
"""

from FILTERS.filter_bank_manager import filter_bank_class
from FILTERS.spectrum import spectrum 
from FILTERS import EAWICA

from threading import Thread, Lock
import time 
import numpy as np

class data_manager_openBCI(Thread):         #Recibe la aplicación

    # Inicializa la aplicación
    def __init__(self, app):
        Thread.__init__(self)               #Inicializa el hilo
        self.app = app                      #Guarda la aplicación
        ### data ###########
        self.all_data_store = np.empty(shape=(self.app.constants.CHANNELS, 0))  #Crea una matriz vacía con la forma:
                                                                                # filas = número de sensores/canales
                                                                                # columnas  = 0
        ########### SHARED QUEUE ###########
        self.app.slots.append(self.append_to_store)                             #Introducir un callback en la lista
        self.filter_bank = filter_bank_class(self.app.constants)                #Enviar las constantes al filtro
        self.filter_bank.update_filters()
        self.spectrum = spectrum(self.app.constants)                            #Enviar las constantes al espectro
        self.muttex = Lock()                   #Asociar el mutex a una variable
     
    def run(self):              #Función del hilo: extraer los datos de la cola y guardarlos en el buffer
        # BUCLE INFINITO
        while True:
            time.sleep(0.005)                      #Espera en segundos
            # Mientras haya datos en la cola, se extraen
            if self.app.constants.CHANNELS == 8:
                while not self.app.queue.empty():
                    self.muttex.acquire()               #Se cierra el mutex
                    sample = self.app.queue.get()       #Se cogen los datos de la cola
                    self.app.buffer.append(sample, 0)   #Se guardan en el buffer
                    self.muttex.release()               #Se desbloquea el mutex

            if self.app.constants.CHANNELS == 16:
                while not (self.app.queue_odd.empty() or self.app.queue_even.empty()):
                    self.muttex.acquire()                       # Se cierra el mutex
                    sample_odd = self.app.queue_odd.get()       # Se cogen los datos de la cola
                    self.app.buffer.append(sample_odd, 1)       # Se guardan en el buffer
                    sample_even = self.app.queue_even.get()     # Se cogen los datos de la cola
                    self.app.buffer.append(sample_even, 2)      # Se guardan en el buffer
                    self.muttex.release()                       # Se desbloquea el mutex

    # Inicializar los filtros
    def init_filters(self):
        self.filter_bank.update_filters()

    # Extraer y filtrar una muestra del buffer
    def get_sample(self): 
        self.muttex.acquire()                                               #Se cierra el mutex
        filtered = self.filter_bank.pre_process(self.app.buffer.get())      #Se aplica el prefiltrado a los datos del buffer
        self.muttex.release()                                               #Se abre el mutex
        return filtered                                                     #Retorna la muestra filtrada

    # Extraer y filtrar una muestra pequeña
    def get_short_sample(self, method): 
        self.muttex.acquire()                              #Se cierra el mutex
        filtered = self.filter_bank.pre_process(self.app.buffer.get())                            #Se aplica el prefiltrado a los datos del buffer
        filtered = filtered[:, int(self.app.constants.pos_ini):int(self.app.constants.pos_end)]      #Se extrae un rango de puntos concreto de la muestra
        # Si se especifica, se aplica el filtro EAWICA
        if method == 'EAWICA':
            try:
                filtered = EAWICA.eawica(filtered, self.app.constants)
            except:
                pass
        self.muttex.release()                              #Se abre el mutex
        return filtered                                    #Se retorna la muestra corta filtrada

    # Calcular el espectro de frecuencias
    def get_powerSpectrum(self, method):
        self.muttex.acquire()                                           #Se cierra el mutex
        filtered = self.filter_bank.pre_process(self.app.buffer.get())  #Se aplica el prefiltrado a los datos del buffer
        freqs, spectra = self.spectrum.get_spectrum(filtered)           #Se calcula el espectro de los datos filtrados
        self.muttex.release()                                           #Se abre el mutex
        return freqs, spectra                                           #Se retorna la frecuencia y el espectro

    # Calcular el espectrograma
    def get_powerSpectrogram(self, method, channel):
        self.muttex.acquire()                                               #Se cierra el mutex
        filtered = self.filter_bank.pre_process(self.app.buffer.get())    #Se aplica el prefiltrado a los datos del buffer
        spectrogram = self.spectrum.get_spectrogram(filtered[channel, :])   #Se calcula el espectrograma del canal especificado la señal filtrada
        self.muttex.release()                                               #Se abre el mutex
        return spectrogram                                                  #Se retorna el espectrograma

    # Añadir datos al banco de datos
    def append_to_store(self):
        sample_data = self.get_short_sample(self.app.constants.METHOD)          #Se extrae una muestra pequeña con el método indicado
        self.all_data_store = np.hstack((self.all_data_store, sample_data))     #Añade la nueva muestra a la matriz ya existente del banco
        self.app.constants.running_window += 1

    # Vaciar banco de datos
    def reset_data_store(self):       
        self.all_data_store = np.empty(shape=(self.app.constants.CHANNELS, 0))  #Se reinicia la matriz del banco de datos poniendo todos los campos a cero
        self.app.constants.running_trial += 1                                   #Incrementa en 1 el valor del TRIAL = nuevo conjunto de medidas
