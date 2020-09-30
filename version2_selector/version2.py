# IMPORTAR MÓDULOS
# Módulos Propios
from COM.trigger_server_2 import trigger_server                         #Recibir y retransmitir datos via TCP/IP
from DYNAMIC import dynamic as Dyn_import                               #Cargar archivos --> OpenFile
from GENERAL.data_manager_openBCI_04 import data_manager_openBCI        #Aplicación de los filtros a las medidas
from LOGGING import logger as log                                       #Modifica el log --> OpenBCI (driver)
from GENERAL.ring_buffer_02 import RingBuffer as buffer                 #Gestiona el buffer de datos de los sensores
from GENERAL.constants_02 import constants                              #Constantes de configuración del proceso --> Buffer, Trig_Server, SaveFile
from COM.open_bci_GCPDS_02 import OpenBCIBoard as openBCI
from GUI.GUI_bci_03 import GUI
from GENERAL.slots_manager import SlotsManager                          #Manejo de Lista de callbacks --> Buffer
from GENERAL.recording_manager_01 import recording_manager              #Grabación de medidas para guardarlos en un archivo EDF

# Módulos Externos
from PyQt5 import QtWidgets
from multiprocessing import Queue, Value



# CREAR APLICACIÓN
class MyApp(QtWidgets.QApplication):

    # Inicialización
    def __init__(self):

        QtWidgets.QApplication.__init__(self, [''])         #Inicia la aplicación de QT

        ############# LOGIC CONTROL ##################
        self.isconnected = Value('b', 1)                    #Devuelve una "Envoltura de Sincronización" de tipo byte con valor 1

        # Iniciar Constantes
        self.constants = constants()

        ######### slots manager for multiple callbacks settings #############
        self.slots = SlotsManager()

        # Iniciar Encolamiento
        self.queue = Queue()
        self.queue_even = Queue()
        self.queue_odd = Queue()

        ##### TRIGGER SERVER ############
        self.trigger_server = trigger_server(self.constants.ADDRESS, self.constants.PORT)

        # Iniciar buffer donde se guardan los datos de los sensores
        self.buffer = buffer(self.constants)
        self.buffer.emitter.connect(self.slots.trigger)     ##### Ejecuta el evento para los callbacks??

        # Iniciar manejo de datos
        self.eeg_dmg = data_manager_openBCI(self)           #Envía toda la clase MYAPP
        self.eeg_dmg.start()

        # Iniciar interfaz TCP/IP para adquisición de datos
        self.recording_manager = recording_manager(self)        #Introduce la propia aplicación

        # Iniciar Aplicación GUI: envía la aplicación completa y una lista de callbacks
        # CALLBACKS: conjunto de acciones ante las que debe dar una respuesta = conexión, adquisición, actualización, guardar o cargar/abrir
        self.gui = GUI(self, callbacks = [self.connection_manager, self.recording_manager.test_acquisition, self.recording_manager.update_state, self.saveFileDialog, self.openFileNameDialog])

        ########## LOGGER ####################
        self.log = log.logger(self.gui)         #Introducir la aplicación GUI previamente creada

        # Iniciar Driver
        self.driver = openBCI(self, self.queue, self.queue_even, self.queue_odd, self.recording_manager.streaming, self.isconnected, self.log)     #Introduce la cola, los estados del streaming y de conexión y el logger
        self.driver.start()

    # Conexión con el dispositivo
    def connection_manager(self):
        # Si no está conectado, intenta conectarse al dispositivo y activa los filtros internos de la tarjeta
        if not self.isconnected.value:
            self.driver.connect()
            self.driver.enable_filters()
        # Si está conectado, se desconecta
        else:
            self.driver.disconnect()

    # Guardar archivo
    def saveFileDialog(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self.gui.MainWindow,"QFileDialog.getSaveFileName()","","EDF Files (*.edf)", options=options)
        if fileName:
            self.constants.PATH = fileName
            self.constants.ispath = True

    # Cargar archivo
    def openFileNameDialog(self, btn):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileType = "PYTHON Files (*.py)"
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self.gui.MainWindow,"QFileDialog.getOpenFileName()","",fileType, options=options)
        #----------------- LOAD AND EXECUTE THE MODULE -----#
        Dyn_import.load_module(fileName, self)

    # Ejecutar aplicación GUI
    def execute_gui(self):
        self.exec()

# EJECUTAR APLICACIÓN
if __name__ == "__main__":      #Si se ejecuta el script, se ejecuta este bloque
    # Crea un objeto MAIN de la clase MYAPP
    main = MyApp()
    # Invoca el método EXECUTE_GUI que ejecuta la aplicación GUI
    main.execute_gui()

