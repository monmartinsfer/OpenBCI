# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759306 
"""

from EDF.writeEDFFile import edf_writter
from multiprocessing import Process

class io_manager():
    
    def __init__(self, app):                            #Recibe la aplicación completa de RECORDING
        self.app = app
        self.edf = edf_writter(self.app.constants)      #Introduce las constantes
        
    # Crear un archivo EDF
    def create_file(self):
        # Se crea un nuevo fichero indicando el nombre = dirección + número de la prueba
        self.edf.new_file(self.app.constants.PATH + '_trial_' + str(self.app.constants.running_trial) + '.edf')
        # Actualiza el texto del logger con la dirección indicando que se ha creado
        self.app.log.update_text('* -- USER ' + self.app.constants.PATH + ' CREATED -- *')

    # Cerrar archivo EDF
    def close_file(self):
        self.edf.close_file()           #Se cierra el archivo
        # Actualiza el texto del logger con la dirección indicando que se ha cerrado
        self.app.log.update_text('* -- USER ' + self.app.constants.PATH + ' CLOSED -- *')

    # Añadir datos al archivo
    #### tarda mucho en guardar, probar hilos o guardar en variable allData hasta terminar registro y luego guardar en archivo
    def append_to_file(self, all_data_store):
        # Si se activa el fichero, se agregan los datos almacenados en el banco de datos al archivo
        if self.app.constants.ispath:
            self.edf.append(all_data_store)
            # Se crea un proceso de escritura sobre el archivo EDF
            p = Process(target=self.edf.writeToEDF())
            p.start()
            
        else:
            print('* -- EDF file path is needed -- *')

    # Escribir una anotación
    def online_annotation(self, notation):      #Recibe la notificación
        # Calcula el instante en el que se ha recibido la notificación:
        # ventana actual * segundos por ventana = segundo actual
        # columna actual del buffer % tamaño de ventana pequeño (ventana de muestreo) / frecuencia de muestreo = milisegundo actual
        instant = self.app.constants.running_window*self.app.constants.SECONDS + (self.app.buffer.cur % self.app.buffer.size_short)/self.app.constants.SAMPLE_RATE
        duration = -1
        event = notation
        self.edf.annotation(instant, duration, event)       #Crear la notificación
