# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759306 
"""

from multiprocessing import Value
from GENERAL.fileIO import io_manager 

class recording_manager:
    
    def __init__(self, app):            #Recibe la aplicación completa de MAIN
        self.streaming = Value('b',0)   #Devuelve una "Envoltura de Sincronización" de tipo byte con valor 0
        self.app = app
        self.io = io_manager(self.app)  #Introduce la aplicación completa al FILEIO

    # Adquisición
    def test_acquisition(self):

        # Si NO está activa la variable de streaming, se inicia el driver y las temporizaciones de las gráficas del GUI
        # Se utiliza para iniciar la conexión con el driver y, por consiguiente, el proceso
        if not self.streaming.value:
            self.app.driver.send_start()
            self.app.gui.eeg_timer.start(self.app.constants.refresh_rate) 
            self.app.gui.eeg_short_timer.start(self.app.constants.short_refresh_rate) 
            self.app.gui.freq_timer.start(self.app.constants.refresh_rate)

        # Si el streaming está activo, se para el driver y las temporizaciones de las gráficas del GUI
        else:
            # stop driver and gui updating
            self.app.driver.send_stop()
            self.app.gui.eeg_timer.stop()   
            self.app.gui.eeg_short_timer.stop() 
            self.app.gui.freq_timer.stop()  

    # Actualizar estado
    def update_state(self, action):           # Recibe una acción

        # Si el streaming NO está activo y se ejecuta la acción de "start", se inicia el proceso de grabación de datos
        if not self.streaming.value and action == 'start':
            # Se actualiza el texto del logger avisando de que se ha iniciado la grabación de datos del conjunto actual
            self.app.log.update_text('Start recording trial: ' + str(self.app.constants.running_trial))
            # Se inicia la ventana de muestreo actual en 0
            self.app.constants.running_window = 0
            # Se crea un nuevo archivo
            self.io.create_file()
            # Se notifica que se ha iniciado la grabación de datos
            self.io.online_annotation(action)
            # Se inicia el driver y las temporizaciones de las gráficas del GUI
            self.app.eeg_dmg.reset_data_store()
            self.app.driver.send_start()
            self.app.gui.eeg_timer.start(self.app.constants.refresh_rate) 
            self.app.gui.eeg_short_timer.start(self.app.constants.short_refresh_rate) 
            self.app.gui.freq_timer.start(self.app.constants.refresh_rate)

        # Si la acción que se recibe es la de "stop", se para el proceso de grabación de datos
        elif action == 'stop':
            # Se actualiza el texto del logger avisando de que se ha parado la grabación de datos del conjunto actual
            self.app.log.update_text('Stop recording trial: ' + str(self.app.constants.running_trial))
            # Se notifica que se ha parado la grabación de datos
            self.io.online_annotation(action)
            # Se para el driver y la actualización del GUI
            self.app.driver.send_stop()
            self.app.gui.eeg_timer.stop()    
            self.app.gui.eeg_short_timer.stop() 
            self.app.gui.freq_timer.stop()  
            # Se agregan los datos medidos al banco de datos, se guardan en el archivo y se cierra
            self.app.eeg_dmg.append_to_store()
            self.io.append_to_file( self.app.eeg_dmg.all_data_store )
            self.io.close_file()

        # Si la acción no es ninguna de ellas, se realiza una notificación y se guarda en la última acción ejecutada
        else:
            self.app.eeg_dmg.online_annotation(action)
            self.app.constants.last_action = action
