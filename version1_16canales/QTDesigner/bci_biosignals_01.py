# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759306 
"""

from PyQt5 import QtCore, QtGui, QtWidgets

# VENTANA DE VISUALIZACIÓN
class Ui_MainWindow(object):

    # Configuración de la pantalla
    def setupUi(self, MainWindow):                      #Recibe la pantalla de visualización DESDE GUI
        MainWindow.setObjectName("MainWindow")          #Le pone un nombre a la pantalla
        MainWindow.resize(1084, 807)                    #Fija el tamaño de la pantalla

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)    #Tamaño FIJO
        sizePolicy.setHorizontalStretch(0)              #Factor de estirado horizontal
        sizePolicy.setVerticalStretch(0)                #Factor de estirado vertical
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())   #Dependencia entre alto-ancho
        MainWindow.setSizePolicy(sizePolicy)            #Aplicar configuración de tamaño

        self.centralwidget = QtWidgets.QWidget(MainWindow)  #Seleccionar widget principal
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)    #Tamaño MAXIMO
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)        #Aplicar el tamaño al widget principal
        self.centralwidget.setObjectName("centralwidget")   #Poner nombre al widgets principal

        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.centralwidget)       #Bloque para alinear en vertical añadido DENTRO de CENTRAL
        self.verticalLayout_6.setObjectName("verticalLayout_6")

        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()                               #Bloque para alinear en horizontal
        self.horizontalLayout_3.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)   #Da valor de tamaño mínimo y máximo
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")

        self.verticalLayout_5 = QtWidgets.QVBoxLayout()                                  #Bloque para alinear en vertical
        self.verticalLayout_5.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)  #Da valor al tamaño mínimo (a no ser que ya haya un valor)
        self.verticalLayout_5.setSpacing(6)                                              #Espaciado entre widgets dentro del bloque
        self.verticalLayout_5.setObjectName("verticalLayout_5")

        self.external_groupBox = QtWidgets.QGroupBox(self.centralwidget)        #Bloque de grupo DENTRO de CENTRAL
        self.external_groupBox.setMinimumSize(QtCore.QSize(250, 60))            #Fija tamaño mínimo
        self.external_groupBox.setMaximumSize(QtCore.QSize(250, 60))            #Fija tamaño máximo
        self.external_groupBox.setAlignment(QtCore.Qt.AlignCenter)              #Alineación CENTRAL
        self.external_groupBox.setObjectName("external_groupBox")

        self.verticalLayout = QtWidgets.QVBoxLayout(self.external_groupBox)     #Bloque vertical DENTRO de GROUPBOX
        self.verticalLayout.setObjectName("verticalLayout")

        self.external_horizontalLayout = QtWidgets.QHBoxLayout()
        self.external_horizontalLayout.setObjectName("external_horizontalLayout")
        #Crea un separador de unas determinadas anchura, altura, escalado horizontal, escalado vertical
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.external_horizontalLayout.addItem(spacerItem)         #Agrega el objeto Separador al interior del bloque

        self.btn_user = QtWidgets.QPushButton(self.external_groupBox)           #Agrega un botón DENTRO de GROUPBOX
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_user.sizePolicy().hasHeightForWidth())
        self.btn_user.setSizePolicy(sizePolicy)                                 #Aplica el escalado al botón
        self.btn_user.setMinimumSize(QtCore.QSize(100, 17))                     #Fija tamaño mínimo del botón
        self.btn_user.setMaximumSize(QtCore.QSize(100, 17))                     #Fija tamaño máximo del botón
        self.btn_user.setObjectName("btn_user")
        self.external_horizontalLayout.addWidget(self.btn_user)                 #Coloca el botón en el siguiente hueco del bloque horizontal

        self.btn_loadScript = QtWidgets.QPushButton(self.external_groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_loadScript.sizePolicy().hasHeightForWidth())
        self.btn_loadScript.setSizePolicy(sizePolicy)
        self.btn_loadScript.setMinimumSize(QtCore.QSize(100, 17))
        self.btn_loadScript.setMaximumSize(QtCore.QSize(100, 17))
        self.btn_loadScript.setObjectName("btn_loadScript")
        self.external_horizontalLayout.addWidget(self.btn_loadScript)
        #Agregamos al final del bloque horizontal otro separador
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.external_horizontalLayout.addItem(spacerItem1)

        self.verticalLayout.addLayout(self.external_horizontalLayout)       #Agrega el bloque horizontal al vertical del GROUPBOX
        self.verticalLayout_5.addWidget(self.external_groupBox)             #Agrega el GROUPBOX al bloque vertical

        self.connect_groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.connect_groupBox.setMinimumSize(QtCore.QSize(250, 100))
        self.connect_groupBox.setMaximumSize(QtCore.QSize(250, 100))
        self.connect_groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.connect_groupBox.setObjectName("connect_groupBox")

        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.connect_groupBox)
        self.verticalLayout_4.setObjectName("verticalLayout_4")

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.gridLayout_8 = QtWidgets.QGridLayout()             #Crea un bloque cuadrícula
        self.gridLayout_8.setObjectName("gridLayout_8")

        self.btn_trigger = QtWidgets.QPushButton(self.connect_groupBox)
        self.btn_trigger.setMinimumSize(QtCore.QSize(70, 17))
        self.btn_trigger.setMaximumSize(QtCore.QSize(70, 17))
        self.btn_trigger.setObjectName("btn_trigger")
        # Agrega el botón a una posición de la cuadrícula: fila, columna, número de filas y número de columnas que abarca
        # Primera celda = ARRIBA IZQUIERDA = posición 0,0
        self.gridLayout_8.addWidget(self.btn_trigger, 0, 1, 1, 1)

        self.btn_connect = QtWidgets.QPushButton(self.connect_groupBox)
        self.btn_connect.setEnabled(True)
        self.btn_connect.setMinimumSize(QtCore.QSize(70, 17))
        self.btn_connect.setMaximumSize(QtCore.QSize(70, 17))
        self.btn_connect.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.btn_connect.setObjectName("btn_connect")
        self.gridLayout_8.addWidget(self.btn_connect, 0, 0, 1, 1)

        self.spinBox = QtWidgets.QSpinBox(self.connect_groupBox)    #Crea un bloque para introducir valores (flecha arriba/abajo para cambiar)
        self.spinBox.setMaximumSize(QtCore.QSize(70, 17))
        self.spinBox.setMinimum(10000)                              #Fija el valor MÍNIMO del selector
        self.spinBox.setMaximum(10099)                              #Fija el valor MÁXIMO del selector
        self.spinBox.setObjectName("spinBox")
        self.gridLayout_8.addWidget(self.spinBox, 1, 1, 1, 1)

        self.btn_start = QtWidgets.QPushButton(self.connect_groupBox)
        self.btn_start.setEnabled(True)                             #Habilita el botón
        self.btn_start.setMinimumSize(QtCore.QSize(70, 17))
        self.btn_start.setMaximumSize(QtCore.QSize(70, 17))
        self.btn_start.setObjectName("btn_start")
        self.gridLayout_8.addWidget(self.btn_start, 1, 0, 1, 1)

        self.horizontalLayout.addLayout(self.gridLayout_8)
        self.verticalLayout_4.addLayout(self.horizontalLayout)
        self.verticalLayout_5.addWidget(self.connect_groupBox)

        self.controls_groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.controls_groupBox.setMinimumSize(QtCore.QSize(250, 165))
        self.controls_groupBox.setMaximumSize(QtCore.QSize(250, 165))
        self.controls_groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.controls_groupBox.setObjectName("controls_groupBox")

        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.controls_groupBox)
        self.verticalLayout_3.setObjectName("verticalLayout_3")

        self.windowsSize_formLayout = QtWidgets.QFormLayout()               #Crea un bloque que gestiona los widgets de entrada
        self.windowsSize_formLayout.setContentsMargins(6, 6, 6, 6)          #Fija los márgenes izq, dch, sup e inf
        self.windowsSize_formLayout.setSpacing(6)                           #Fija el espaciado entre elementos
        self.windowsSize_formLayout.setObjectName("windowsSize_formLayout")

        self.channels_label = QtWidgets.QLabel(self.controls_groupBox)
        self.channels_label.setObjectName("channels_label")
        self.windowsSize_formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.channels_label)

        self.channels_comboBox = QtWidgets.QComboBox(self.controls_groupBox)
        self.channels_comboBox.setObjectName("channels_comboBox")
        self.windowsSize_formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.channels_comboBox)

        self.butterOrder_label = QtWidgets.QLabel(self.controls_groupBox)   #Crea una etiqueta
        self.butterOrder_label.setObjectName("butterOrder_label")
        self.windowsSize_formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.butterOrder_label)

        self.butterOrder_spinBox = QtWidgets.QSpinBox(self.controls_groupBox)   #Selector del orden del filtro Butterworth
        self.butterOrder_spinBox.setMinimum(5)
        self.butterOrder_spinBox.setMaximum(300)
        self.butterOrder_spinBox.setProperty("value", 5)                     #Da un valor a la característica VALUE
        self.butterOrder_spinBox.setObjectName("butterOrder_spinBox")
        # Introduce un widget en el bloque en la fila y con el rol especificados
        self.windowsSize_formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.butterOrder_spinBox)     #Rol = campo

        self.WindowsSize_label = QtWidgets.QLabel(self.controls_groupBox)
        self.WindowsSize_label.setObjectName("WindowsSize_label")
        self.windowsSize_formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.WindowsSize_label)       #Rol = etiqueta

        self.WindowsSize_spinBox = QtWidgets.QSpinBox(self.controls_groupBox)   #Selector del tamaño de la ventana de muestreo
        self.WindowsSize_spinBox.setMinimum(1)
        self.WindowsSize_spinBox.setMaximum(60)
        self.WindowsSize_spinBox.setProperty("value", 6)
        self.WindowsSize_spinBox.setObjectName("WindowsSize_spinBox")
        self.windowsSize_formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.WindowsSize_spinBox)

        self.frequency_comboBox = QtWidgets.QComboBox(self.controls_groupBox)       # Crea un bloque que despliega las opciones que se pueden seleccionar
        self.frequency_comboBox.setCurrentText("")
        self.frequency_comboBox.setObjectName("frequency_comboBox")
        self.windowsSize_formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.frequency_comboBox)

        self.frequency_label = QtWidgets.QLabel(self.controls_groupBox)
        self.frequency_label.setObjectName("frequency_label")
        self.windowsSize_formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.frequency_label)

        self.filtering_label = QtWidgets.QLabel(self.controls_groupBox)
        self.filtering_label.setObjectName("filtering_label")
        self.windowsSize_formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.filtering_label)

        self.filtering_comboBox = QtWidgets.QComboBox(self.controls_groupBox)
        self.filtering_comboBox.setObjectName("filtering_comboBox")
        self.windowsSize_formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.filtering_comboBox)

        self.verticalLayout_3.addLayout(self.windowsSize_formLayout)

        self.controls_horizontalLayout = QtWidgets.QHBoxLayout()
        self.controls_horizontalLayout.setObjectName("controls_horizontalLayout")

        self.Spectrogram_radioButton = QtWidgets.QRadioButton(self.controls_groupBox)   #Crea un botón con múltiples opciones exclusivas
        self.Spectrogram_radioButton.setObjectName("Spectrogram_radioButton")
        self.controls_horizontalLayout.addWidget(self.Spectrogram_radioButton)

        self.Spectrogram_comboBox = QtWidgets.QComboBox(self.controls_groupBox)
        self.Spectrogram_comboBox.setObjectName("Spectrogram_comboBox")
        self.controls_horizontalLayout.addWidget(self.Spectrogram_comboBox)

        self.verticalLayout_3.addLayout(self.controls_horizontalLayout)
        self.verticalLayout_5.addWidget(self.controls_groupBox)

        self.log_groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.log_groupBox.setMinimumSize(QtCore.QSize(250, 200))
        self.log_groupBox.setMaximumSize(QtCore.QSize(250, 16777215))
        self.log_groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.log_groupBox.setObjectName("log_groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.log_groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        self.logger = QtWidgets.QPlainTextEdit(self.log_groupBox)           #Crea un campo de texto editable
        self.logger.setReadOnly(True)                                       #Campo solo de lectura
        self.logger.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)    #Modo de interactuar con el usuario al mostrar un mensaje
        self.logger.setObjectName("logger")

        self.verticalLayout_2.addWidget(self.logger)
        self.verticalLayout_5.addWidget(self.log_groupBox)
        self.horizontalLayout_3.addLayout(self.verticalLayout_5)

        self.verticalLayout_8 = QtWidgets.QVBoxLayout()
        self.verticalLayout_8.setObjectName("verticalLayout_8")

        self.EEG_signals_groupBox = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.EEG_signals_groupBox.sizePolicy().hasHeightForWidth())
        self.EEG_signals_groupBox.setSizePolicy(sizePolicy)
        self.EEG_signals_groupBox.setTitle("")
        #Alineación principal, izquierda o centrada vertical
        self.EEG_signals_groupBox.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.EEG_signals_groupBox.setObjectName("EEG_signals_groupBox")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.EEG_signals_groupBox)
        self.verticalLayout_7.setObjectName("verticalLayout_7")

        self.EEG_plot = PlotWidget(self.EEG_signals_groupBox)               #Crea un campo de gráficas
        self.EEG_plot.setObjectName("EEG_plot")

        self.verticalLayout_7.addWidget(self.EEG_plot)
        self.verticalLayout_8.addWidget(self.EEG_signals_groupBox)

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        self.frequency_groupbox = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frequency_groupbox.sizePolicy().hasHeightForWidth())
        self.frequency_groupbox.setSizePolicy(sizePolicy)
        self.frequency_groupbox.setTitle("")
        self.frequency_groupbox.setAlignment(QtCore.Qt.AlignCenter)
        self.frequency_groupbox.setObjectName("frequency_groupbox")

        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.frequency_groupbox)
        self.verticalLayout_9.setObjectName("verticalLayout_9")

        self.Frequency_plot = PlotWidget(self.frequency_groupbox)
        self.Frequency_plot.setObjectName("Frequency_plot")
        self.verticalLayout_9.addWidget(self.Frequency_plot)
        self.horizontalLayout_2.addWidget(self.frequency_groupbox)

        self.spectroplot_groupBox = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spectroplot_groupBox.sizePolicy().hasHeightForWidth())
        self.spectroplot_groupBox.setSizePolicy(sizePolicy)
        self.spectroplot_groupBox.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.spectroplot_groupBox.setTitle("")
        self.spectroplot_groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.spectroplot_groupBox.setObjectName("spectroplot_groupBox")

        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.spectroplot_groupBox)
        self.verticalLayout_10.setObjectName("verticalLayout_10")

        self.Emotions_plot = PlotWidget(self.spectroplot_groupBox)
        self.Emotions_plot.setObjectName("Emotions_plot")

        self.verticalLayout_10.addWidget(self.Emotions_plot)
        self.horizontalLayout_2.addWidget(self.spectroplot_groupBox)
        self.verticalLayout_8.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3.addLayout(self.verticalLayout_8)
        self.verticalLayout_6.addLayout(self.horizontalLayout_3)
        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(MainWindow)               #Crea una barra de menú horizontal
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1084, 20))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)           #Crea una barra horizontal que muestra información del estado
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)                      #Traduce los textos
        QtCore.QMetaObject.connectSlotsByName(MainWindow)   #Busca todos los elementos asociados al objeto indicado y
                                                            #conecta sus señales (signals) a acciones (slots)

    # Traduce todos los textos a partir de los archivos de traducción instalados
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        #Se especifica el lugar donde está el texto, el texto a traducir
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.external_groupBox.setTitle(_translate("MainWindow", "External controls"))
        self.btn_user.setText(_translate("MainWindow", "Set Users"))
        self.btn_loadScript.setText(_translate("MainWindow", "Load script"))
        self.connect_groupBox.setTitle(_translate("MainWindow", " Connect to the OpenBCI device"))
        self.btn_trigger.setText(_translate("MainWindow", "Trigger"))
        self.btn_connect.setText(_translate("MainWindow", "Connect"))
        self.btn_start.setText(_translate("MainWindow", "Start"))
        self.controls_groupBox.setTitle(_translate("MainWindow", "Electrophysiological signals controls"))
        self.channels_label.setText(_translate("MainWindow", "Number of channels"))
        self.butterOrder_label.setText(_translate("MainWindow", "Butter filter order"))
        self.WindowsSize_label.setText(_translate("MainWindow", "Windows size [seconds]"))
        self.frequency_label.setText(_translate("MainWindow", "Frequency range"))
        self.filtering_label.setText(_translate("MainWindow", "Filtering method"))
        self.Spectrogram_radioButton.setText(_translate("MainWindow", "Spectrogram"))
        self.log_groupBox.setTitle(_translate("MainWindow", "Log viewer"))

from pyqtgraph import PlotWidget
