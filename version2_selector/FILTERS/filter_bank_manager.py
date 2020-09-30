# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759306 
"""

from scipy.signal import butter, iirnotch, filtfilt
import numpy as np
import pywt


class filter_bank_class():

    # Inicializa el filtro
    def __init__(self, constants):      #Recibe las constantes DESDE data_manager O DESDE EAWICA
        self.constants = constants

    # Crea los filtros de notch y de butterworth y guarda sus parámetros
    def update_filters(self):
        self.b0, self.a0 = self.notch_filter()
        self.b, self.a = self.butter_bandpass()

    # Ejecuta el pre-proceso de filtrado
    def pre_process(self, sample):      #Recibe las muestras almacenadas en el BUFFER DESDE data_manager
        sample = np.array(sample)       #Las transforma en una matriz
        [fil, col] = sample.shape
        sample_processed = np.zeros([fil, col])     #Crea una matriz del mismo tamaño que la de las muestras

        # Para cada fila (correspondiente a cada sensor) coge los datos y los filtra
        for i in range(fil):
            data = sample[i, :]
            data = data - np.mean(data) 	    #Resta la media de los datos para eliminar la componente continua
            # Si hay un limite inferior y uno superior, aplica el filtro de Butterworth
            if self.constants.LOWCUT != None and self.constants.HIGHCUT != None:
                data = self.butter_bandpass_filter(data)
            data = data*1000000+(i+1)*100       #Eliminar muestras extra y escalar??
            sample_processed[i, :] = data       #Guarda la medida filtrada en otra matriz
  
        return sample_processed         #Devuelve la medida filtrada

    # Diseña el filtro de Notch
    def notch_filter(self):     # f0 50Hz, 60 Hz
        Q = 30.0                #Factor de calidad del filtro

        # Calcula y devuelve los parámetros del filtro
        b0, a0 = iirnotch(self.constants.NOTCH, Q, self.constants.SAMPLE_RATE)
        return b0,a0

    # Diseña el filtro de Butterworth
    def butter_bandpass(self):
        nyq = 0.5 * self.constants.SAMPLE_RATE
        low = self.constants.LOWCUT / nyq
        high = self.constants.HIGHCUT / nyq

        # Calcula y devuelve los parámteros del filtro de Butterworth con las frecuencias de corte, el orden y el tipo de filtro
        b, a = butter(self.constants.ORDER, [low, high], btype='band')
        return b, a

    # Aplica el filtro de Butterworth GENÉRICO previamente creado
    def butter_bandpass_filter(self, data):
        # Aplica el filtro de Notch y después el de Butterworth a los datos
        noth_data = filtfilt(self.b0, self.a0, data)
        band_passed_data = filtfilt(self.b, self.a, noth_data)
        return band_passed_data

    # Aplica el filtro de Butterworth ESPECÍFICO
    def butter_bandpass_specific_filter(self, data, lowcut, highcut, Fs, order):    #Recibe parámetros para crear un nuevo filtro
        # Aplica el filtro de Notch genérico previamente creado
        noth_data = filtfilt(self.b0, self.a0, data)
        # Crea un nuevo filtro Butterworth específico con los parámetros recibidos y lo aplica a los datos tratados con el Notch
        nyq = 0.5 * Fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order , [low, high], btype='band')
        band_passed_data = filtfilt(b, a, noth_data)
        return band_passed_data

    # Recibe los rangos de filtrado y aplica el filtro específico para esas bandas
    def filter_bank(self, signal, Fs, filter_ranges, order=5):
        filterbank = []
        for [lowcut,highcut] in filter_ranges:
            y = self.butter_bandpass_specific_filter(signal, lowcut, highcut, Fs, order)
            filterbank.append(y)
        return np.asarray(filterbank)

    # Aplica el filtro EAWICA paso-banda
    def eawica_wavelet_band_pass(self, signal, wavelet):
    
        import copy
        levels = 8

        coeffs = pywt.wavedec(signal, wavelet, mode='symmetric', level=levels, axis=-1)     #Aplica una DWT multinivel
        # Crea copias de la DWT para todas las bandas de frecuencias
        gamma_coeffs = copy.copy(coeffs)
        beta_coeffs = copy.copy(coeffs)
        alpha_coeffs = copy.copy(coeffs)
        theta_coeffs = copy.copy(coeffs)
        delta_coeffs = copy.copy(coeffs)
        
        # Extrae la banda de frecuencias GANMA anulando las demás
        for i in range(levels+1):
            if i != 7 and i != 8:
                gamma_coeffs[i] = np.zeros(gamma_coeffs[i].shape)
        # Extrae la banda de frecuencias BETA anulando las demás
        for i in range(levels+1):
            if i != 6:
                beta_coeffs[i] = np.zeros(beta_coeffs[i].shape)
        # Extrae la banda de frecuencias ALPHA anulando las demás
        for i in range(levels+1):
            if i != 5:
                alpha_coeffs[i] = np.zeros(alpha_coeffs[i].shape)
        # Extrae la banda de frecuencias THETA anulando las demás
        for i in range(levels+1):
            if i != 4:
                theta_coeffs[i] = np.zeros(theta_coeffs[i].shape)
        # Extrae la banda de frecuencias DELTA anulando las demás
        for i in range(levels+1):
            if i != 1 and i != 2 and i!= 3: 
                delta_coeffs[i] = np.zeros(delta_coeffs[i].shape)
                
        # Se reconstruye la señal original para cada banda de frecuencias
        gamma = pywt.waverec(gamma_coeffs, wavelet)
        beta = pywt.waverec(beta_coeffs, wavelet)
        alpha = pywt.waverec(alpha_coeffs, wavelet)
        theta = pywt.waverec(theta_coeffs, wavelet)
        delta = pywt.waverec(delta_coeffs, wavelet)
    
        return [gamma, beta, alpha, theta, delta]

    # Diseña el filtro EAWICA
    def wavelet_filter_aicaw(self, data, wavelet):
    
        import copy
        levels = 8
        coeffs = pywt.wavedec(data, wavelet, mode='symmetric', level=levels, axis=-1)       #Aplica una DWT multinivel
        # Crea copias de la DWT para todas las bandas de frecuencias
        gamma_coeffs = copy.copy(coeffs)
        beta_coeffs = copy.copy(coeffs)
        alpha_coeffs = copy.copy(coeffs)
        theta_coeffs = copy.copy(coeffs)
        delta_coeffs = copy.copy(coeffs)

        # Extrae la banda de frecuencias GANMA anulando las demás
        for i in range(levels+1):
            if i != 6:
                beta_coeffs[i] = np.zeros(beta_coeffs[i].shape)
                # Extrae la banda de frecuencias BETA anulando las demás
        for i in range(levels+1):
            if i != 5:
                beta_coeffs[i] = np.zeros(beta_coeffs[i].shape)
        # Extrae la banda de frecuencias ALPHA anulando las demás
        for i in range(levels+1):
            if i != 4:
                alpha_coeffs[i] = np.zeros(alpha_coeffs[i].shape)
        # Extrae la banda de frecuencias THETA anulando las demás
        for i in range(levels+1):
            if i != 3:
                theta_coeffs[i] = np.zeros(theta_coeffs[i].shape)
        # Extrae la banda de frecuencias DELTA anulando las demás
        for i in range(levels+1):
            if i != 1 and i != 2:
                delta_coeffs[i] = np.zeros(delta_coeffs[i].shape)
           
        return [gamma_coeffs, beta_coeffs, alpha_coeffs, theta_coeffs, delta_coeffs]