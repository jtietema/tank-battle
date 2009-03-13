import socket
import select
import threading
import time

class ClientSocket(threading.Thread):
    '''Client socket for sending messages'''
    def __init__(self, adress):
        super(ClientSocket, self).__init__()
        self.messages = []
        self.incoming = []
        self.adress = adress
    
    def run(self):
        s = socket.socket()
        s.connect(self.adress)
        s.setblocking(0)
        self.running = True
        while self.running:
            read, write, error = select.select([s],[s],[])
            if len(read) > 0:
                data = s.recv(4096).strip()
                if not data:
                    self.running = False
                else:
                    self.process_buffer(data)
                    print 'RECV: ' + data
            elif len(write) > 0 and len(self.messages) > 0:
                for m in self.messages:
                    self.messages.remove(m)
                    s.send(m + '\n')
                    print 'SEND: ' + m
        s.shutdown(socket.SHUT_RDWR)
        s.close()
    
    def process_buffer(self, data):
        '''Does all processing of the incomming data'''
        self.incoming.append(data.split('\n'))
    
    def get_messages(self):
        '''Returns all incoming messages'''
        pass
    
    def send(self, msg):
        '''Send a message to the server'''
        self.messages.append(msg)
    
    def stop(self):
        '''Stop the socket and thread'''
        self.running = False


soc = ClientSocket(('localhost',8008))

soc.send('Hi')
soc.start()
soc.send('something')
soc.send('another something')
time.sleep(10)
soc.send('done')
time.sleep(1)
soc.stop()
soc.join()
print 'Exit'