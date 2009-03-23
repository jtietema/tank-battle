import socket
import sys
import select
import threading

# TODO: refactor running loop to share code with client class
# TODO: make messages & incomming thread safe

class ServerSocket(threading.Thread):
    '''Represents one connection with a client'''
    def __init__(self, socket):
        super(ServerSocket, self).__init__()
        self.messages = ['Welcome', 'to the server']
        self.socket = socket
        self.socket.setblocking(0)
        self.running = True

    def run(self):
        '''start communication with the client'''
        print 'Connecting client'
        while self.running:
            # check what we can do
            read, write, error = select.select([self.socket],[self.socket],[],0)
            if len(read) > 0:
                # the socket is avalible for reading
                data = self.socket.recv(4096).strip()
                if not data:
                    # the connection appears dead, disconnect
                    self.running = False
                else:
                    print 'RECV: ' + data
            elif len(write) > 0 and len(self.messages) > 0:
                # the socket is avalible for writing, send messages
                m = self.messages[0]
                self.messages.remove(m)
                self.socket.send(m + '\n')
                print 'SEND: ' + m
            elif len(error) > 0:
                # the socket is in error, disconnect
                self.running = False
        self.socket.close()
        print 'Disconnecting client'
    
    def send(self, msg):
        '''Send a message to the client'''
        self.messages.append(msg)

class Server():
    '''A server that accepts connections from multiple clients'''
    def __init__(self, port):
        self.adress = ('', port)
        self.clients = []
    
    def run(self):
        '''start the server'''
        s = socket.socket()
        s.bind(('', 8008))
        s.listen(5)
        while True:
            # pass the incomming connection to a worker thread
            client_socket,addr = s.accept()
            thread = ServerSocket(client_socket)
            thread.start()
            self.clients.append(thread) # TODO make sure we remove the thread somewhere when its finished

server = Server(8008)
server.run()
