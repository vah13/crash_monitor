import socket

import array

import time

from timeout import timeout


def connect_with_socket(adress, port):
    _socket = socket.socket()
    _socket.connect((adress, int(port)))
    return _socket

@timeout(3)
def send_data(_socket, row, timeout=3):
    _socket.send(row)
    _socket.settimeout(timeout)


def close_socket(_socket):
    _socket.close()

def recieve_data(_socket):
    return _socket.recv(1024*1024 )

crash_data = []

def main():
    global crash_data
    while True:
            try:
                sock = socket.socket()
                sock.bind(('', 13131))
                sock.listen(3)
                sock.settimeout(3)
                conn, addr = sock.accept()
                #print '1'
                _remote_data = recieve_data(conn)
                #print '2'
                crash_data.append(_remote_data.encode('hex'))
                #print crash_data
                #print '3'
                _sap_socket = connect_with_socket("127.0.0.1",3201)
                #print '4'
                send_data(_sap_socket,_remote_data)
                #print '5'
                close_socket(_sap_socket)
                time.sleep(3)
            except Exception, ex:
                print ex