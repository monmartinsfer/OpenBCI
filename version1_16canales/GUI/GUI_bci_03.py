# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759306 
"""
#%%
from QTDesigner.bci_biosignals_01 import Ui_MainWindow as ui
from PyQt5 import QtWidgets, QtCore
from qwt.qt.QtGui import QFont
from qwt import  QwtText
import pyqtgraph as pg
import numpy as np
import time

class GUI():

    # Inicialización
    def __init__(self, app, callbacks):         #Recibe la aplicación completa y una lista de callbacks DESDE MAIN
        
        self.app = app

        # Gestión de los datos
        self.curves_EEG = []                #Lista para los valores de la gráfica EEG
        self.lr = None
        self.spectrogram_Img = None         #Imagen del espectrograma: para el espectrograma de un único canal
        self.curves_Freq = []               #Lista para los valores de la gráfica del espectrograma de todos los canales
        self.curves_EEG_short = []          #Lista para los valores del EEG empleando la muestra corta

        # Diseño de la pantalla de visualización (UI)
        self.MainWindow = QtWidgets.QMainWindow()               #Crea la pantalla de visualización
        self.bci_graph = ui()                                   #Crea el objeto de la pantalla
        self.bci_graph.setupUi(self.MainWindow)                 #Envía la pantalla de visualización para su inicialización
        self.bci_graph.WindowsSize_spinBox.setRange(0, 12)
        # Ejecución de las funciones de la pantalla de visualización
        self.initLongTermViewCurves()
        self.initShortTermViewCurves()
        self.initFrequencyView()
        self.set_plots()
        self.initChannelComboBox()
        self.initFrequencyComboBox()
        self.initFilteringComboBox()
        self.initSpectrogramComboBox()
        self.load_style()
        self.MainWindow.show()              #Ejecución de la pantalla de visualización
        # Activa el antialiasing para gráficas más limpias/precisas
        pg.setConfigOptions(antialias=True)

        # Activar callbacks
        # Si se pulsa el botón de CONECTAR, se ejecuta la función del primer elemento de la lista de Callbacks = ConnectionManager (MAIN)
        self.bci_graph.btn_connect.clicked.connect(callbacks[0])
        # Si se pulsa el botón de START, se ejecuta la función del segundo elemento de la lista de Callbacks = TestAdquisition (RECORDING)
        self.bci_graph.btn_start.clicked.connect(callbacks[1])
        # Si se pulsa el botón de TRIGGER, se ejecuta la función de trigger con el tercer elemento de la lista de Callbacks = UpdateState (RECORDING)
        self.bci_graph.btn_trigger.clicked.connect(lambda: self.launch_trigger_server(callbacks[2]))
        # Si se pulsa el botón de USER, se ejecuta la función del cuarto elemento de la lista de Callbacks = SaveFileDialog (MAIN)
        self.bci_graph.btn_user.clicked.connect(callbacks[3])
        # Si se pulsa el botón de LOADSCRIPT, se ejecuta la función del último elemento de la lista de Callbaks = OpenFileNameDialog (MAIN)
        self.bci_graph.btn_loadScript.clicked.connect(callbacks[4])

        # Si se cambia el número de canales, se ejecuta la función Set_Channels
        self.bci_graph.channels_comboBox.currentIndexChanged.connect(lambda: self.set_channels())
        # Si se cambia el rango de frecuencias, se ejecuta la función Set_Frequency
        self.bci_graph.frequency_comboBox.currentIndexChanged.connect(lambda: self.set_frequency())
        # Si se cambia el valor del filtrado, se ejecuta la función Set_Filtering
        self.bci_graph.filtering_comboBox.currentIndexChanged.connect(lambda: self.set_filtering())
        # Si cambia el valor del tamaño de ventana de muestreo, se ejecuta la función Set_SampleSize
        self.bci_graph.WindowsSize_spinBox.valueChanged.connect(lambda: self.set_sampleSize())
        # Si cambia el valor del orden del filtro de Butterworth, se ejecuta la función Set_Order
        self.bci_graph.butterOrder_spinBox.valueChanged.connect(lambda: self.set_order())
        # Si cambia el canal del espectrograma, se ejecuta la función Set_Channel_Spectrogram
        self.bci_graph.Spectrogram_radioButton.toggled.connect(lambda: self.set_channel_spectrogram())
        self.bci_graph.Spectrogram_comboBox.currentIndexChanged.connect(lambda: self.set_channel_spectrogram())

        # Crear temporizadores para actualizar las gráficas
        # Temporizador del gráfico de las señales de los sensores = Electroencefaloframa
        self.eeg_timer = QtCore.QTimer()
        self.eeg_timer.setTimerType(QtCore.Qt.PreciseTimer)     #Tipo de temporizador que tiene precisión de milisegundos
        self.eeg_timer.timeout.connect(self.eeg_update)         #Función se ejecuta cuando la temporización finaliza

        # Temporizador del EEG empleando muestra corta
        self.eeg_short_timer = QtCore.QTimer()
        self.eeg_short_timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.eeg_short_timer.timeout.connect(self.eeg_short_update)

        # Temporizador del gráfico de frecuencias
        self.freq_timer = QtCore.QTimer()
        self.freq_timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.freq_timer.timeout.connect(self.freq_update)        


    # REPRESENTACIÓN GRÁFICA
    # Gráfica de las medidas de los sensores del electroencefalograma EEG
    def eeg_update(self):
        sample = self.app.eeg_dmg.get_sample()          #Coge la muestra del DATA MANAGER
        # Para cada canal, coge el dato de la fila correspondiente y lo agrega a la lista de medidas de la gráfica EEG

        for i in range(self.app.constants.CHANNELS):
            self.curves_EEG[i].setData(sample[i, :])


    # Gráfica del espectro de frecuencias
    def freq_update(self):
        #freqs, spectra = self.app.eeg_dmg.get_powerSpectrum(self.app.constants.METHOD)  #Calcula el espectro
        # Comprueba si el RadioButton del espectrograma tiene una selección = un canal
        if self.bci_graph.Spectrogram_radioButton.isChecked():
            # Selecciona el canal cuyo nombre se haya escogido en el botón
            channel = self.app.constants.CHANNEL_IDS.index(self.bci_graph.Spectrogram_comboBox.currentText())
            # Calcula el espectro del canal seleccionado
            spectrogram = self.app.eeg_dmg.get_powerSpectrogram(self.app.constants.METHOD, channel)

            ini = int(self.app.constants.pos_ini/self.app.constants.SAMPLE_RATE)
            # Selecciona la imagen que se mostrará: espectrograma calculado, permitiendo el ajuste automático
            self.spectrogram_Img.setImage(spectrogram[:, :].T, autoLevels=True)
        # Si no se ha seleccionado un canal, se calcula el espectrograma de todos
        else:
            freqs, spectra = self.app.eeg_dmg.get_powerSpectrum(self.app.constants.METHOD)

            # Para cada canal se guarda su respectivo espectro en escala logarítmica para todas las frecuencias
            for i in range(self.app.constants.CHANNELS):
                self.curves_Freq[i].setData(freqs, np.log10(spectra[i, :]))

    # Gráfica del EEG usando una muestra pequeña
    def eeg_short_update(self):
        sample = self.app.eeg_dmg.get_short_sample(self.app.constants.METHOD)

        for i in range(self.app.constants.CHANNELS):
            self.curves_EEG_short[i].setData(sample[i, :])
            
    # Gestor de Eventos (TRIGGER)
    def launch_trigger_server(self, callback):                  #Recibe el UpdateState (RECORDING)
        #Si hay un socket creado, lo cierra
        if self.app.trigger_server.activated:
            self.app.trigger_server.close_socket()
        #Si no hay un socket creado, lo crea, inicia la comunicación y envía el callback
        else:
            self.app.trigger_server.create_socket()   
            self.app.trigger_server.start()
            self.app.trigger_server.new_COM1.connect(callback) 
            
    # Acciones de los botones
    # Seleccionar canal del espectrograma
    def set_channel_spectrogram(self):
        self.initFrequencyView()

    def set_channels(self):
        if self.app.recording_manager.streaming.value:
            self.eeg_short_timer.stop()
            self.eeg_timer.stop()
            self.freq_timer.stop()

        channels = self.bci_graph.channels_comboBox.currentText()
        if channels == '8':
            self.app.driver.channels_8()
        if channels == '16':
            self.app.driver.channels_16()

        self.app.buffer.reset(self.app.constants.WINDOW)
        self.app.eeg_dmg.reset_data_store()
        self.initSpectrogramComboBox()
        self.initLongTermViewCurves()
        self.initShortTermViewCurves()
        self.initFrequencyView()
        self.set_plots(reset=True)
        self.load_style()

        if self.app.recording_manager.streaming.value:
            self.eeg_short_timer.start(self.app.constants.short_refresh_rate)
            self.eeg_timer.start(self.app.constants.refresh_rate)
            self.freq_timer.start(self.app.constants.refresh_rate)

    # Seleccionar el valor de la frecuencia
    def set_frequency(self):
        # Extrae el texto de la opción del rango de frecuencias seleccionada y ejecuta el cambio en COSNTANTS
        self.app.constants.set_filter_range(self.bci_graph.frequency_comboBox.currentText())  
        # Si se fija un límite inferior, se actualizan los parámetros de los filtros
        if self.app.constants.LOWCUT != None:
            self.app.eeg_dmg.init_filters()

    # Seleccionar el filtro
    def set_filtering(self):
        # Si se está realizando una comunicación, se detienen las temporizaciones para realizar el cambio
        if self.app.streaming.value:
            self.eeg_timer.stop()      
            self.freq_timer.stop()
            self.eeg_short_timer.stop()
        # Se actualiza el campo del método de filtrado en CONSTANTS con el texto extraído de la opción escogida
        self.app.constants.update('method', self.bci_graph.filtering_comboBox.currentText())
        # Si se estaba realizando una comunicación, se reinician las temporizaciones
        if self.app.streaming.value:
            self.eeg_timer.start(self.app.constants.refresh_rate) 
            self.freq_timer.start(self.app.constants.refresh_rate) 
            self.eeg_short_timer.start(self.app.constants.short_refresh_rate) 

    # Seleccionar la frecuencia de muestreo
    def set_sampleSize(self):
        # Se actualiza el campo de la frecuencia de muestreo en CONSTANTS con el valor seleccionado
        self.app.constants.update('seconds', int(self.bci_graph.WindowsSize_spinBox.value()))
        self.app.eeg_dmg.buffer.reset(self.app.constants.WINDOW)        # Se resetea el buffer con el nuevo tamaño
        self.set_plots(reset = True)            # Se resetea la gráfica

    # Seleccionar orden del filtro de Butterworth
    def set_order(self):
        # Se actualiza el campo del orden del filtro de Butterworth en CONSTANTS con el valor seleccionado
        self.app.constants.update('order', int(self.bci_graph.butterOrder_spinBox.value()))
        
    # Configuración de la aplicación

    def eeg_short_view(self):
        # Guarda los valores límite de la región actual = permite saber el tamaño de la ventana
        self.app.constants.pos_ini, self.app.constants.pos_end = self.lr.getRegion()
        # Indica los valores del eje X = tamaño de la ventana
        self.bci_graph.Emotions_plot.setXRange(0, int(self.app.constants.pos_end - self.app.constants.pos_ini))
        self.bci_graph.Emotions_plot.setLimits(xMin=0, xMax=int(self.app.constants.pos_end - self.app.constants.pos_ini))

    # GRÁFICAS
    def set_plots(self, reset = False):
        channels = self.app.constants.CHANNEL_IDS

        # Gráfica EEG
        self.bci_graph.EEG_plot.setLabel('bottom', 'Samples', units='n')        #Etiqueta del eje inferior
        # Selecciona los elementos a mostrar
        if self.app.constants.CHANNELS == 8:
            self.bci_graph.EEG_plot.getAxis('left').setTicks([[(100, channels[0]), (200, channels[1]), (300, channels[2]),
                                                               (400, channels[3]), (500, channels[4]), (600, channels[5]),
                                                               (700, channels[6]), (800, channels[7])]])
            self.bci_graph.EEG_plot.setYRange(0, 900)
        elif self.app.constants.CHANNELS == 16:
            self.bci_graph.EEG_plot.getAxis('left').setTicks([[(100, channels[0]), (200, channels[1]), (300, channels[2]),
                                                               (400, channels[3]), (500, channels[4]), (600, channels[5]),
                                                               (700, channels[6]), (800, channels[7]), (900, channels[8]),
                                                               (1000, channels[9]), (1100, channels[10]), (1200, channels[11]),
                                                               (1300, channels[12]), (1400, channels[13]), (1500, channels[14]),
                                                               (1600, channels[15])]])
            self.bci_graph.EEG_plot.setYRange(0, 1700)
        # Fija los valores de los ejes
        self.bci_graph.EEG_plot.setXRange(0, self.app.constants.LARGE_WINDOW)
        self.bci_graph.EEG_plot.setLimits(xMin=0, xMax=self.app.constants.LARGE_WINDOW)
        self.bci_graph.EEG_plot.showGrid(True, True, alpha=0.3)  # Mostrar cuadrícula

        # Configuración de la región
        if not reset:
            # Se crea la región con los valores actuales de las posiciones
            self.lr = pg.LinearRegionItem([self.app.constants.pos_ini, self.app.constants.pos_end])
            self.bci_graph.EEG_plot.addItem(self.lr)
            self.lr.sigRegionChanged.connect(self.eeg_short_view)
            self.eeg_short_view()
        # Si se pide el reseteo opor modificar la frecuencia de muestreo, se crea una nueva región con los nuevos valores
        else:
            self.lr.setRegion([self.app.constants.pos_ini,self.app.constants.pos_end])

        # Configuración de la gráfica EmotionsPlot
        self.bci_graph.Emotions_plot.setLabel('bottom', 'Samples', units='n')
        if self.app.constants.CHANNELS == 8:
            self.bci_graph.Emotions_plot.getAxis('left').setTicks([[(100, channels[0]), (200, channels[1]), (300, channels[2]),
                                                               (400, channels[3]), (500, channels[4]), (600, channels[5]),
                                                               (700, channels[6]), (800, channels[7])]])
            self.bci_graph.Emotions_plot.setYRange(0, 900)
        elif self.app.constants.CHANNELS == 16:
            self.bci_graph.Emotions_plot.getAxis('left').setTicks([[(100, channels[0]), (200, channels[1]), (300, channels[2]),
                                                               (400, channels[3]), (500, channels[4]), (600, channels[5]),
                                                               (700, channels[6]), (800, channels[7]), (900, channels[8]),
                                                               (1000, channels[9]), (1100, channels[10]), (1200, channels[11]),
                                                               (1300, channels[12]), (1400, channels[13]), (1500, channels[14]),
                                                               (1600, channels[15])]])
            self.bci_graph.Emotions_plot.setYRange(0, 1700)

        self.bci_graph.Emotions_plot.setXRange(0, int(self.app.constants.pos_end - self.app.constants.pos_ini))
        self.bci_graph.Emotions_plot.showGrid(True, True, alpha = 0.3)
        self.bci_graph.Emotions_plot.setLimits(xMin=0, xMax=int(self.app.constants.pos_end - self.app.constants.pos_ini))

    # Aplicar formato a las gráficas
    def load_style(self):        
        self.styleQwtPlot('EEG', self.bci_graph.EEG_plot)
        self.styleQwtPlot('Frequency', self.bci_graph.Frequency_plot)
        self.styleQwtPlot('Emotion estimation', self.bci_graph.Emotions_plot)
        
        with open("QTDesigner/style.css") as f:
            self.app.setStyleSheet(f.read())

    # Formato de las gráficas
    def styleQwtPlot(self, name, elem):
        font = QFont()
        font.setPixelSize(24)
        title = QwtText(name)
        title.setFont(font)
        elem.setTitle(title)

    def initChannelComboBox(self):
        self.bci_graph.channels_comboBox.addItems(['8', '16'])

    # Agregar opciones a la lista de rangos de frecuencia
    def initFrequencyComboBox(self):
        self.bci_graph.frequency_comboBox.addItems(['Full','Delta','Theta','Alpha','Beta','Gamma'])

    # Agregar opciones a la lista de sensores para el espectrograma
    def initSpectrogramComboBox(self):
        self.bci_graph.Spectrogram_comboBox.clear()
        self.bci_graph.Spectrogram_comboBox.addItems(self.app.constants.CHANNEL_IDS)

    # Agregar elementos a la lista de métodos de filtrado
    def initFilteringComboBox(self):
        self.bci_graph.filtering_comboBox.addItems(['Butterworth','EAWICA','AICAW'])

    # GRÁFICA EEG
    def initLongTermViewCurves(self):
        self.curves_EEG = []
        self.bci_graph.EEG_plot.clear()
        # Para cada canal, se crea una curva de la gráfica
        for i in range(self.app.constants.CHANNELS):
            c = pg.PlotCurveItem(pen = (i, self.app.constants.CHANNELS*1.3))
            c.setPos(0, 0)
            self.bci_graph.EEG_plot.addItem(c)  #Agregar la curva al widget
            self.curves_EEG.append(c)           #Se asocia los valores a la gráfica

    # GRÁFICA EEG con mjuestra corta
    def initShortTermViewCurves(self):
        self.curves_EEG_short = []
        self.bci_graph.Emotions_plot.clear()

        for i in range(self.app.constants.CHANNELS):
            c = pg.PlotCurveItem(pen = (i, self.app.constants.CHANNELS*1.3))
            c.setPos(0, 0)
            self.bci_graph.Emotions_plot.addItem(c)
            self.curves_EEG_short.append(c)

    # GRÁFICA DE ESPECTROGRAMA
    def initFrequencyView(self):
        self.curves_Freq = []                           #Crear listas para los datos de frecuencia
        self.bci_graph.Frequency_plot.clear()           #Limpiar el widget de frecuencia

        # Si se ha seleccionado un canal para el espectrograma
        if self.bci_graph.Spectrogram_radioButton.isChecked():
            self.bci_graph.Frequency_plot.showGrid(True, True, alpha = 0)
            self.bci_graph.Frequency_plot.setLogMode(False, False)                  #No muestra la etiqueta
            self.bci_graph.Frequency_plot.setLabel('left', 'Frequency', units='Hz')
            self.bci_graph.Frequency_plot.setLabel('bottom', "Samples", units='n')
            
            self.spectrogram_Img = pg.ImageItem()       #Crea la imagen para guardar el espectrograma
            self.bci_graph.Frequency_plot.addItem(self.spectrogram_Img)     #Añade la imagen al widget

            pos = np.array([0.0, 0.5, 1.0])
            color = np.array([[0,0,0,255], [255,128,0,255], [255,255,0,255]], dtype=np.ubyte)
            map = pg.ColorMap(pos, color)               #Asocia unos valores a los colores
            lut = map.getLookupTable(0.0, 1.0, 256)     #Devuelve una tabla de búsqueda de colores
            self.spectrogram_Img.setLookupTable(lut)    #Aplica la tabla de colores al espectrograma

        # Si no se ha seleccionado un canal
        else:   
            ### FREQUENCY Plot settings ###
            self.bci_graph.Frequency_plot.showGrid(True, True, alpha = 0.3)
            self.bci_graph.Frequency_plot.setLogMode(False, True)                       #Muestra las etiquetas
            self.bci_graph.Frequency_plot.setLabel('left', 'Amplitude', units='dB')
            self.bci_graph.Frequency_plot.setLabel('bottom', "Frequency", units='Hz')
            # Para cada canal, crea una curva de la gráfica
            for i in range(self.app.constants.CHANNELS):
                c = pg.PlotCurveItem(pen=i)
                self.bci_graph.Frequency_plot.addItem(c)            #Se añade la gráfica al widget
                self.curves_Freq.append(c)                          #Se asocia los valores a la gráfica
    
            
        
        

