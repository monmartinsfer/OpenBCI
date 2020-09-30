# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759306 
"""
#%%
from PyQt5 import QtCore 
import numpy as np

class RingBuffer(QtCore.QThread):           #Recibe las constantes DESDE main
    """ class that implements a not-yet-full buffer """
    emitter = QtCore.pyqtSignal()           #Crea una señal

    # Inicializa el buffer
    def __init__(self, constants, parent=None):
        super(RingBuffer, self).__init__(parent)
        self.constants = constants                          #Guarda las constantes
        self.channels = self.constants.CHANNELS             #Guarda el número de canales
        self.max = self.constants.LARGE_WINDOW              #Guarda el marco de visualización = número de columnas
        self.size_short = self.constants.WINDOW             #Guarda la ventana de muestreo
        self.data = np.zeros((self.channels, self.max))     #Matriz de ceros: filas = canales, columnas = ventana máxima
        self.cur = self.max                                 #Crea una variable para el número de columnas
        self.full = False                                   #Inicia vacío

    # Resetea el buffer
    def reset(self, size_short):
        self.size_short = size_short                        #Se le indica un nuevo tamaño de ventana pequeño
        self.data = np.zeros((self.constants.CHANNELS, self.max))     #Vuelve a poner la matriz a ceros
        self.cur = self.max

    # Añade un dato al final del buffer
    def append(self, x, packet):                                    #Recibe los datos de todos los canales de una vez en forma de vector FILA DESDE DATA_MANAGER

        if self.constants.CHANNELS == 8:
            self.cur = self.cur % self.max                      #Calcula la primera columna vacía
            if packet == 0:
                self.data[:, self.cur] = np.asarray(x).transpose()  #Transforma los datos en un vector COLUMNA,
                                                                #lo transforma en columna y lo introduce en la primera columna vacía
        elif self.constants.CHANNELS == 16:
            self.cur = self.cur % self.max
            if packet == 1:
                self.data[:8, self.cur] = np.asarray(x).transpose()
            if packet == 2:
                self.data[8:, self.cur] = np.asarray(x).transpose()

        self.cur = self.cur+1                               #Se guarda la siguiente fila

        # Si se ha llegado a la columna correspondiente al tamaño de ventana pequeño (ventana de muestreo), se emite toda la información
        if (self.cur % self.size_short) == 0:
            self.emitter.emit()  
            print('full myfriend: ', self.cur, 'short window size: ', self.size_short)

    # Devuelve la lista de datos por orden cronológico del más antiguo al más nuevo
    def get(self):
        """ Return a list of elements from the oldest to the newest. """
        return np.hstack((self.data[:, self.cur:], self.data[:, :self.cur]))      #Concatena los datos en horizontal
