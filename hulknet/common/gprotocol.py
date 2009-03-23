import xdrlib
import struct

from twisted.internet.protocol import Protocol

class GProtocol(Protocol):
    MSG_ERROR = -99
    """A Protocol for game messages.
    """
    def connectionMade(self):
        self.packetBuffer = ""
        self.packetSize = 0
        self.errorMsg = ""
        self.errorId = 0
        self.msgMap = {}

    def registerHandler(self, msgId, handler):
        self.msgMap[msgId] = handler
        
    def processPacket(self, data):
        """Process a packet from the connection. Sends an error
        if the handler method fails.
        """
        unpacker = xdrlib.Unpacker(data)
        msgId = unpacker.unpack_int()
        handlerMethod = self.msgMap.get(msgId)
        print "handling:", msgId, handlerMethod        
        if handlerMethod:
            try:
                if not handlerMethod(unpacker):
                    self.sendError()
            except:
                print "Exception occurred in msg handler"
                raise
        else:
            print "Unknown network message", msgId
        
    def dataReceived(self, data):
        """this method received data from the network. It has two states,
            - receiving a packet size
            - receiving the rest of a packet
        """
        self.packetBuffer += data

        # process all the packets in the data.
        while self.packetBuffer:
            
            if self.packetSize == 0:
                # reading the size
                if len(self.packetBuffer) < 4:
                    return
                else:
                    self.packetSize = struct.unpack('i', self.packetBuffer[:4])[0] + 4
                    print "Got packet size of :", self.packetSize

            if len(self.packetBuffer) >= self.packetSize:
                # we have a full packet
                packetData = self.packetBuffer[4:self.packetSize]
                self.packetBuffer = self.packetBuffer[self.packetSize:]
                self.packetSize = 0
                self.processPacket(packetData)
            else:
                print "Read %d bytes.. waiting." % len(self.packetBuffer)
                return
        
    def writePacker(self, packer):
        """Helper method for writing the contents of a packer"""
        buffer = packer.get_buffer()
        sizeBuffer = struct.pack('i', len(buffer))
        self.transport.write(sizeBuffer)
        self.transport.write(buffer)
        
    def sendError(self):
        print "Error:", self.errorId, self.errorMsg
        packer = xdrlib.Packer()
        packer.pack_int(MSG_ERROR)
        packer.pack_int(self.errorId)
        packer.pack_string(self.errorMsg)
        self.writePacker(packer)
