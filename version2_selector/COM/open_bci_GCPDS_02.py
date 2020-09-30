# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759306 
"""

from COM.OpenBCISample import OpenBCISample

from multiprocessing import Process, Value
import serial
import struct
import time
import atexit
import logging
import threading
import sys
import glob

# DEFINICIÓN DE CONSTANTES
SAMPLE_RATE = 250.0  # Hz Frecuencia de muestreo.
START_BYTE = 0xA0  # Byte que indica el inicio de un paquete de datos = 1010 0000 = 160
END_BYTE = 0xC0  # Byte que indica el final de un paquete de datos = 1100 0000 = 192


# Se encarga de realizar la conexión con la tarjeta OpenBci.
# Define las funciones para desempaquetar los datos, comunicarse con la tarjeta, iniciar y detener el envío de datos.
class OpenBCIBoard(Process):

    # Inicialización: recibe del MAIN la cola, el logger, los estados del streaming y de la conexión. Además fija un
    # valor de puerto nulo, el tiempo de espera y la velocidad de conexión.
    def __init__(self, app, queue, queue_even, queue_odd, streaming, isconnected, log, port=None, baud=115200, filter_data=True, timeout=1):
        # Inicialización del proceso
        Process.__init__(self)
        # Inicialización de variables
        self.app = app
        self.baudrate = baud                        # Velocidad de comunicación serie
        self.timeout = timeout                      # Tiempo de espera
        self.port = port                            # Puerto Serial
        self.filtering_data = filter_data           # Estado de los filtros internos de la tarjeta
        self.eeg_channels_per_sample = 8            # Canales de sensores de la tarjeta
        self.aux_channels_per_sample = 3            # Canales auxiliares de la tarjeta
        self.read_state = 0                         # ESTADO DE LECTURA = la lectura de los datos se realiza por pasos
        self.attempt_reconnect = False
        self.last_reconnect = 0
        self.reconnect_freq = 5
        self.packets_dropped = 0                    # Número de paquetes perdidos
        self.scaling_output = True                  # Aplicar escala a la medida
        self.log = True
        self.log_packet_count = 0
        self.scale_fac_uVolts_per_count = 2.23517444553071e-08      # Factor de conversión microVoltios --> Doc OPENBCI
        self.scale_fac_accel_G_per_count = 0.002                    # Factor de conversión del acelerómetro
        self.queue = queue                          # Cola (8 canales)
        self.queue_odd = queue_odd                      # Cola paquete impar (16 canales)
        self.queue_even = queue_even                     # Cola paquete par (16 canales)
        self.streaming = streaming                  # Estado del streaming recibido desde MAIN quien lo recibe de RECORDING
        self.isconnected = isconnected              # Estado de conexión
        self.log = log                              # Logger

        self.canales = Value('d', 8)

        # Cuando se ejecuta la salida del programa, finaliza la comunicación
        atexit.register(self.disconnect)

        # Si no está conectado a ningún puerto, intenta buscarlo al inicializar
        try:
            if not self.port:
                self.port = self.find_port()
            print("Connecting to V3 at port %s" % (self.port))
        except:
            if not self.port:
                self.port = self.find_port()
            print("Connecting to V3 at port %s" % (self.port))

        # Se define la comunicación serial con el puerto encontrado a la velocidad especificada y durante un tiempo de espera concreto
        self.ser = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=self.timeout)
        print("Serial established...")

    # Código de ejecución del proceso
    def run(self):
        # BUCLE INFINITO
        while True:
            # Si el streaming está activado, se leen los datos recibidos al puerto serial y se guardan en la cola
            if self.streaming.value:

                if self.canales.value == 8.0:
                    try:
                        sample = self._read_serial_binary()
                        self.queue.put(sample.channel_data)         #Introduce en la cola SOLO las medidas de los sensores
                    except:
                        print('Driver Error while reading serial binaries')
                if self.canales.value == 16.0:
                    try:
                        sample = self._read_serial_binary()
                        if (sample.id % 2) == 0:
                            self.queue_even.put(sample.channel_data)         #Introduce en la cola SOLO las medidas de los sensores
                        else:
                            self.queue_odd.put(sample.channel_data)
                    except:
                        print('Driver Error while reading serial binaries')
            # Si es streaming está desactivado, mientras haya datos en la cola, se extraen
            else:
                if self.canales.value == 8.0:
                    while not self.queue.empty():
                        self.queue.get()
                if self.canales.value == 16.0:
                    while not self.queue_even.empty():
                        self.queue_even.get()
                    while not self.queue_odd.empty():
                        self.queue_odd.get()

    # Solicitud de PARADA
    def send_stop(self):
        self.streaming.value = False        # Se desactiva el streaming
        self.ser.write(b's')                # Envía al puerto serie un byte S = indica a la tarjeta que finalice la conexión
        self.log.update_text('Streaming: ' + str(self.streaming.value))     # Actualiza el texto del logger indicando que se ha desactivado el streaming

    # Solicitud de INICIO
    def send_start(self):
        self.streaming.value = True     # Activa el streaming
        self.ser.write(b'b')            # Envía al puerto serie un byte B = indica a la tarjeta que inicie el envío de datos
        self.check_connection()         # Comprueba la conexión
        self.log.update_text('Streaming: ' + str(self.streaming.value))  # Actualiza el texto del logger indicando que se ha activado el streaming

    # CONECTAR CON EL DISPOSITIVO
    def connect(self):
        self.log.update_text("Connecting to V3 at port %s" % (self.port))       # Actualiza el texto del logger indicando que se está conectando al puerto
        self.ser = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=self.timeout)      # Se define la comunicación serial con el puerto encontrado
                                                                                                    # a la velocidad especificada y durante un tiempo de espera concreto
        self.log.update_text("Serial established...")  # Actualiza el texto del logger indicando que se ha conectado al puerto

        time.sleep(2)  # Pausa de 2 segundos

        self.log.update_text(str(self.ser.write(
            b'v')))  # Actualiza el texto del logger indicando el byte V enviado al puerto = indica a la tarjeta que realice un reseteo

        time.sleep(1)  # Pausa de 1 segundo

        self.print_incoming_text()      # Imprimir el mensaje recibido desde la tarjeta
        self.isconnected.value = True   # Se indica que se ha conectado al dispositivo

    # DESCONECTAR CON EL DISOSITIVO
    def disconnect(self):
        # Si la comunicación serial está abierta, se cierra
        if self.ser.isOpen():
            self.ser.close()
            self.log.update_text(
                'Serial closed')  # Se actualiza el texto del logger indicando que se ha finalizado la conexión
            self.isconnected.value = False  # Se indica que de ha desconectado del dispositivo

    # Activar filtros internos de la tarjeta
    def enable_filters(self):
        self.ser.write(b'f')  # Envía al puerto serie un byte F = indica a la tarjeta que active los filtros internos
        self.filtering_data = True  # Indica que se han activado los filtros internos de la tarjeta

    # Desactivar los filtros internos de la tarjeta
    def disable_filters(self):
        self.ser.write(b'g')  # Envía al puerto serie un byte G = indica a la tarjeta que desactive los filtros internos
        self.filtering_data = False  # Indica que se han desactivado los filtros internos de la tarjeta

    # Proceso de lectura del byte
    def read(self, n):  # Indica el número de bytes de lectura
        bb = self.ser.read(n)  # Se realiza la lectura del número de bytes especificados
        # Si no hay ningún dato, se informa de que el dispositivo parece estancado y se cierra el programa de Python
        if not bb:
            print('Device appears to be stalled. Quitting...')
            sys.exit()
            raise Exception('Device Stalled')
            sys.exit()
            return '\xFF'
        # Si hay un dato, lo retorna
        else:
            return bb

    # LECTURA DE DATOS DE SENSORES:
    # El formato de los bytes enviados por la tarjeta Cyton es el siguiente:
    # Byte 1 = cabecera = 0xA0
    # Byte 2 = Número de muestra
    # Bytes (3-5, 6-8, 9-11, 12-14, 157, 18,20, 21,23, 24,26) = Medidas de los sensores = 3 bytes/sensor
    # Bytes 27-32 = datos auxiliares (dependen del valor de la cola)
    # Byte 33 = cola = 0xC0-OxCF --> se empleará el 0xC0
    # Si la cola es 0xC0, los bytes auxiliares 27-32 = AX1,AX0,AY1,AY0,AZ1,AZ0 = medidas del acelerómetro
    def _read_serial_binary(self, max_bytes_to_skip=3000):  # Se fija un máximo de 3000 bytes para desechar antes de encontrar el de inicio
        # Para el rango de bytes a desechar se busca el byte de inicio
        #if self.eeg_channels_per_sample == 8:
            for rep in range(max_bytes_to_skip):
                # BIT DE INICIO e ID DEL PAQUETE
                # Si el estado de lectura es 0 = se realiza la lectura de 1 byte (Byte1 = cabecera)
                if self.read_state == 0:
                    b = self.read(1)

                    # Se desensambla el byte leído en el formato B, transformándolo a INT
                    # Comprueba si el primer elemento de la lista de bytes desempaquetados (solo hay uno) coincide con el con el de inicio
                    if struct.unpack('B', b)[0] == START_BYTE:
                        # Si se han desechado bytes, se indica cuántos se han desechado antes de encontrar el de inicio
                        if (rep != 0):
                            print('Skipped %d bytes before start found' % (rep))
                            rep = 0  # Se reinicia el número de bytes desechados
                        # ID del paquete: se desensambla el byte leído (Byte2 = número de muestra) en formato B, transformándolo en INT
                        packet_id = struct.unpack('B', self.read(1))[0]  #Se extrae el primer número
                        log_bytes_in = str(packet_id)  #Se crea una cadena STRING en la que se van introduciendo los bytes

                        self.read_state = 1  #Se pasa a la siguiente fase de lectura CUANDO ENCUENTRA EL BYTE DE INICIO Y SU ID

                # MEDIDAS DE LOS CANALES
                # Si el estado de lectura es 1 = se crea una lista para las medidas de los canales
                elif self.read_state == 1:
                    channel_data = []

                    # Se recorren todos los canales
                    for c in range(self.eeg_channels_per_sample):
                        literal_read = self.read(3)                             #En cada canal se leen los 3 bytes
                        unpacked = struct.unpack('3B', literal_read)            #Se desempaquetan en formato 3B,
                                                                                #transformando los 3 bytes en UCHART
                                                                                #y metiéndolos en una lista
                        log_bytes_in = log_bytes_in + '|' + str(literal_read)   #Se incluyen los bytes en la cadena STRING

                        # Se aplica el COMPLEMENTO A DOS: enteros NEGATIVOS
                        # El número de combinaciones en complemento a dos es la mitad: 8 bits = 127 positivos + 0 + 128 negativos
                        if (unpacked[0] > 127):
                            # PREFIJO NEGATIVO = unos
                            pre_fix = bytes(bytearray.fromhex('FF'))            #Transforma el STRING en hexadecimal a BYTE
                        else:
                            # PREFIJO POSITIVO = ceros
                            pre_fix = bytes(bytearray.fromhex('00'))
                        # Se añade el prefijo a la lectura realizada para distinguir positivo o negativo
                        literal_read = pre_fix + literal_read
                        # Guarda el elemento desempaquetado en formato >i, transformándolo en BIG-ENDIAN INT y teniendo en cuenta el signo
                        # BIG-ENDIAN es el orden de byte = depende del sistema operativo --> sys.byteorder
                        # MI SISTEMA OPERATIVO ES LITTLE-ENDIAN
                        myInt = struct.unpack('>i', literal_read)[0]

                        # Si se activa el escalado, aplica el factor de escala de microvoltios al valor medido y lo añade a la lista de valores
                        if self.scaling_output:
                            channel_data.append(myInt * self.scale_fac_uVolts_per_count)
                        else:
                            channel_data.append(myInt)

                    self.read_state = 2         #Se pasa a la siguiente fase de lectura CUANDO ACABA CON TODOS LOS CANALES

                # MEDIDAS DEL ACELERÓMETRO
                # Si el estado de lectura es 2: se crea una lista para los valores auxiliares = medidas del acelerómetro
                elif self.read_state == 2:
                    aux_data = []

                    # Se recorren todos los bytes auxiliares: los 6 se leen por parejas, por lo que se recorre 3 veces
                    for a in range(self.aux_channels_per_sample):

                        # Se leen los byes or parejas (AX1+AX0/AY1+AY0/AZ1+AZ0), se desempaquetan en formato BIG-ENDIAN SHORT
                        # MI SISTEMA OPERATIVO ES LITTLE-ENDIAN
                        acc = struct.unpack('>h', self.read(2))[0]
                        log_bytes_in = log_bytes_in + '|' + str(acc)        #Se agregan los bytes a la cadena de STRING

                        # Si el escalado está activo, se aplica el factor de conversión del acelerómetro
                        if self.scaling_output:
                            aux_data.append(acc * self.scale_fac_accel_G_per_count)
                        else:
                            aux_data.append(acc)

                    self.read_state = 3      #Se pasa a la siguiente fase de lectura CUANDO ACABA CON LOS 3 EJES DEL ACELERÓMETRO

                # BYTE DE CIERRE
                # Si el estado de lectura es 3 = se lee el último byte, se desempaqueta en formato 'B', transformándolo en UCHART
                elif self.read_state == 3:
                    val = struct.unpack('B', self.read(1))[0]
                    log_bytes_in = log_bytes_in + '|' + str(val)    #Se agrega el byte a la cadena STRING

                    # Se actualiza el estado de lectura para iniicar la lectura del siguiente paquete al terminar el actual
                    self.read_state = 0
                    # Si el byte leído es el de cola, se envían los 3 componentes a SAMPLE
                    if (val == END_BYTE):
                        sample = OpenBCISample(packet_id, channel_data, aux_data)
                        # Reinicia el valor del número de paquetes perdidos porque ha sido capaz de leer un paquete correctamente
                        self.packets_dropped = 0
                        return sample               #Retorna con la muestra encapsulada en SAMPLE

                    # Si el byte NO es el de cola, se invoca un mensaje DEBUG y se incrementa el número de paquetes perdidos
                    else:
                        logging.debug(log_bytes_in)
                        self.packets_dropped = self.packets_dropped + 1

    # Aviso: imprime un aviso concreto
    def warn(self, text):
        print("Warning: %s" % text)

    # Lectura de mensaje
    def print_incoming_text(self):
        line = ''
        # Espera de 1 segundo a que el dispositivo envíe datos
        time.sleep(1)

        # Si el serial está en espera, crear una cadena y leer los caracteres que llegan
        if self.ser.inWaiting():
            line = ''
            c = ''
            # Busca la secuencia de fin '$$$'.
            while '$$$' not in line:
                c = self.ser.read().decode('utf-8')     #Leer un caracter
                line += c                               #Agregarlo a la cadena
            print(line)
        # Si no está en espera, indidcar que no hay mensaje
        else:
            self.warn("No Message")

    # Muestra las configuraciones registradas por la tarjeta
    def print_register_settings(self):

        self.ser.write(b'?')        #Envía al puerto serie un byte ? = indica a la tarjeta que envíe la información sobre su configuración
        time.sleep(0.5)             #Espera de medio segundo a recibir la respuesta
        self.print_incoming_text()  #Imprimir el mensaje recibido por la tarjeta

    # Comprobar conexión
    def check_connection(self, interval=2, max_packets_to_skip=10):     #Se le indica el número máximo de paquetes que se pueden perder
        # Si los paquetes perdidos superan el máximo admisible, hay fallos de conexión y se intenta reconectar
        if self.packets_dropped > max_packets_to_skip:
            self.reconnect()

        # Un hilo que ejecuta la función de reconexión cuando finaliza el intervalo indicado
        threading.Timer(interval, self.check_connection).start()

    # Reconexión
    def reconnect(self):
        self.packets_dropped = 0        #Reinicia el valor del número de paquetes perdidos
        print('Reconnecting')
        self.stop()                     #Parar el proceso
        time.sleep(0.5)
        self.ser.write(b'v')            #Envía al puerto serie un byte V = indica a la tarjeta que realice un reseteo
        time.sleep(0.5)
        self.ser.write(b'b')            #Envía al puerto serie un byte B = indica a la tarjeta que inicie el envío de datos
        time.sleep(0.5)

    # Encontrar puerto serie conectado
    def find_port(self):
        print('Searching Board...')

        # Crea una lista de los nombres de los puertos serie dependiendo del sistema operativo
        # Sistema WINDOWS: puertos COM
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        # Sistema LINUX o UNIX+MICROSOFT: puertos /dev/ttyUSB
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = glob.glob('/dev/ttyUSB*')           #Encuentra los pathnames con el patrón indicado
        # Sistema UNIX+APPLE: puertos /dev/tty.usbserial
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.usbserial*')
        # Si no es ninguno de los anteriores, no busca los puertos
        else:
            print('Error finding ports on your operating system')

        openbci_port = ''
        # Recorre toda la lista de puertos
        for port in ports:
            # Se conecta a cada puerto
            try:
                s = serial.Serial(port=port, baudrate=self.baudrate, timeout=self.timeout)
                # Si consigue escribir en el puerto (envía un byte V al puerto serie = solicita un reinicio a la tarjeta), guarda el puerto
                if s.write(b'v') == 1:
                    openbci_port = port
                s.close()           #Cierra la comunicación
            except:
                pass
        # Si no ha encontrado ningún puerto viable, imprime el aviso
        if openbci_port == '':
            print('Cannot find OpenBCI port. Try again!!')
            return False            #Retorna un false
        else:
            return openbci_port     #Retorna el puerto detectado

    def channels_8(self):
        self.ser.write(b'c')
        time.sleep(0.5)
        self.app.constants.CHANNELS = 8
        self.app.constants.CHANNEL_IDS = ['F1', 'F2', 'C3', 'C4', 'P7', 'P8', 'O1', 'O2']
        self.app.constants.NDIMS = 8
        self.canales.value = 8

    def channels_16(self):
        self.ser.write(b'C')
        time.sleep(0.5)
        self.app.constants.CHANNELS = 16
        self.app.constants.CHANNEL_IDS = ['F1', 'F2', 'C3', 'C4', 'P7', 'P8', 'O1', 'O2',
                                          'F7', 'F8', 'F3', 'F4', 'T7', 'T8', 'P3', 'P4']
        self.app.constants.NDIMS = 16
        self.canales.value = 16

    # Comprueba que el puerto detectado sea de OPEN_BCI
    def openbci_id(self, serial):
        line = ''
        # Espera a que el dispositivo envíe datos
        time.sleep(2)

        # Si el puerto está epserando, crea una cadena y un carácter
        if serial.inWaiting():
            line = ''
            c = ''
            # Busca la secuencia de fin '$$$'
            while '$$$' not in line:
                c = serial.read().decode('utf-8')       #Lee un caracter
                line += c                               #Lo incorora a la cadena
            # Si en la cadena encuentra el patrón OpenBCI, significa que el puerto es correcto
            if "OpenBCI" in line:
                return True         #Retorna un TRUE
        return False                #Si no está esperando o no es un dispositivo OPEN_BCI, retorna FALSE
