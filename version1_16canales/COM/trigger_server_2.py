# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 10.5281/zenodo.3759306 
"""

from PyQt5 import QtCore #conda install pyqt

import socket
import sys

class trigger_server(QtCore.QThread):           #Recibe la dirección IP y el Puerto DESDE main

    new_COM1 = QtCore.pyqtSignal(str)           #Crea una señal

    # Inicialización: guarda las variables Dirección y Puerto recibidas DESDE MAIN
    def __init__(self, address, port, parent=None):
        super(trigger_server, self).__init__(parent)
        self.address = address
        self.port = port
        self.activated = False              #Inicia desactivado

    # Crear socket: nodo de red para enviar y recibir datos
    def create_socket(self):
        self.activated = True               #Al invocar se activa
        # Crea un nodo TCP/IP
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Asocia la Dirección y el Puerto al nodo
        server_address = (self.address, self.port)
        print(sys.stderr, 'starting up on %s port %s' % server_address)
        self.sock.bind(server_address)
        
    # Ejecuta la conexión a la red
    def run(self):
        # Comprueba conexiones entrantes
        print('socket is listening!')
        self.sock.listen(1)
        # Mientras está activado, intenta iniciar comunicación
        while self.activated:
            print(sys.stderr, 'waiting for a connection')
            # Intenta conectarse a no ser que ya esté ocupado
            try:
                self.connection, client_address = self.sock.accept()
            except:
                print(sys.stderr, 'Cannot accept connection due to a closed socket state.')
                break
            # Si se conecta, intenta recibir datos
            try:
                print(sys.stderr, 'connection from', client_address)

                # Recibe los datos en pequeños bloques y los retransmite hasta que no quedan datos
                while True:
                    print('entro')
                    data = self.connection.recv(128)            #Lee los datos
                    print(data.decode())
                    # Si el dato es distinto de 'vacío', lo retransmite con la nueva señal
                    if data != b'':
                        self.new_COM1.emit(data.decode())
                    # Si hay un dato, lo recibe
                    if data:
                        print(sys.stderr, 'received "%s"' % data)
                   # Si no hay dato, cierra la comunicación
                    else:
                        print(sys.stderr, 'no more data from', client_address)
                        break
            except:
                print('Error while listening')
            # Invoca el cierre del socket
            finally:
                self.close_socket()

    # Cierra el nodo, de forma que no se admiten más comunicaciones
    def close_socket(self):  
        self.activated = False  
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        print('socket is closed!')

