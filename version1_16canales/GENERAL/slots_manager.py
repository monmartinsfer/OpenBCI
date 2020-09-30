# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759306 
"""
#%%

class SlotsManager:

    # Inicializa la lista de callbacks
    def __init__(self):
        self.callbacks = []

    # Ejecuta los callbacks de la lista
    def trigger(self):
        for callback in self.callbacks:
            callback()
            print(callback)
#        [callback() for callback in self.callbacks]

    # Añade un slot a la lista de callbacks
    def append(self, slot):
        self.callbacks.append(slot)
        print(slot)

        
