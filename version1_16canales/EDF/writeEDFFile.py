# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759306 
"""

from __future__ import division, print_function, absolute_import

import os
import pyedflib           #Archivos EDF = European Data Format

class edf_writter:
    
    def __init__(self, constants):              #Recibe las constantes de FILEIO
        self.constants = constants

    # Crea un nuevo archivo
    def new_file(self, path):                   #Recibe una dirección donde guardar el archivo
        data_file = os.path.join('.', path)     #Incluye la dirección en el PATH de python
        # Crea un nuevo archivo con el nombre, el número de canales y el tipo
        self.file = pyedflib.EdfWriter(data_file, self.constants.CHANNELS, file_type=pyedflib.FILETYPE_EDFPLUS)
        
        self.channel_info = []          #Crea una lista de canales para guardar la información de cada canal
        self.data_list = []             #Crea una lista de datos para guardar los datos medidos de cada canal

    # Añade los datos almacenados en el banco de datos
    def append(self, all_data_store):
        # Para cada canal crea un diccionario con su etiqueta, la dimensión, la frecuencia de muestreo, los valores máximo y mínimo medidos y los límites máximo y mínimo del canal analógico.
        for channel in range(self.constants.CHANNELS):
            ch_dict = {'label': self.constants.CHANNEL_IDS[channel], 'dimension': 'uV', 'sample_rate': self.constants.SAMPLE_RATE, 'physical_max': all_data_store[channel,:].max(), 'physical_min': all_data_store[channel,:].min(), 'digital_max': 32767, 'digital_min': -32768, 'transducer': '', 'prefilter':''}
            self.channel_info.append(ch_dict)                   #Guarda la información del canal en la lista de canales
            self.data_list.append(all_data_store[channel,:])    #Guarda los datos del canal en la lista de datos

    # Escribir en el fichero EDF
    def writeToEDF(self):
        self.file.setSignalHeaders(self.channel_info)       #Escribir el encabezado de la señal = información de los canales
        self.file.writeSamples(self.data_list)              #Escribir las muestras

    # Escribir una anotación
    def annotation(self, instant, duration, event):             #Recibe el instante, la duración y el evento que se produce para anotarlo en una notificación
        self.file.writeAnnotation(instant, duration, event)

    # Cerrar archivo
    def close_file(self):
        self.file.close()   #Cerrar el archivo en uso
        del self.file       #Eliminar los datos almacenados en el archivo

    # Indicar que se ha eliminado el archivo
    def __del__(self):
        print("deleted")
