import xdrlib
import struct

class Packer(xdrlib.Packer):
    def pack_uint(self, x):
        """Overwritten, because the normal implementation raised a DeprecationWarning
        in Python 2.5.1."""
        self.__buf.write(struct.pack('>l', x))
    
    pack_int = pack_uint