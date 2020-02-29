import socket
import thread
import sys
import queue
from ast import literal_eval
from copy import deepcopy

def handle(conn_addr):
    print("Someone Connected")
    time.sleep(4)
    print("And now I die")
  
def check_messages():
    ret = deepcopy(self.message_buffer)
    self.message_buffer = Queue()
    return ret
    
def process_message(data):
    return literal_eval(data)

self.message_buffer = Queue()

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 10000)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(6)

while True:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)
        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(16)
            process_message(data)
            self.message_buffer.put(data)
            print('received {!r}'.format(data))
            if data:
                print('sending data back to the client')
                connection.sendall(str(data)[::-1].encode())
            else:
                print('no data from', client_address)
                break

    finally:
        # Clean up the connection
        connection.close()