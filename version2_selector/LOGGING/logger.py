# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759306 
"""


class logger():
    # Inicializa la aplicación GUI
    def __init__(self, gui):
        self.text = ''
        self.gui = gui

    # Actualiza el texto del logger que aparece en la visualización
    def update_text(self, text):            #Recibe el texto de FILEIO
        self.gui.bci_graph.logger.appendPlainText(text)
