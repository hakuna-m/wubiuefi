"""Compressed Data RFC 2440.2.3, 2440.5.6

A compressed data packet simply contains OpenPGP message data in a
single packet. In other words, a signature, public key, signed
message or any other valid message type (see rfc2440 10.2) can be
encapsulated in a single compressed data packet. Normally, all this
data is, um, compressed ..but it is also permissible to package
uncompressed data in the "compressed" data packet.

Operations on a compressed data packet normally follow this pattern:

    1. decompress compressed data (if necessary)
    2. re-evaluate data as an OpenPGP message
    3. repeat as needed for nested compressed data packets

Decompressing Data

    The compressed data in `_comp_d` can be decompressed and
    retrieved via the data attribute (see above). However, the
    decompressed data is not an instance attribute. Instead, it
    calls the appropriate decompression function and returns the
    result. Therefore, it's probably best to save the decompressed
    data elsewhere instead of making repeated calls to 
    compressed_data_obj.data.
"""
import zlib

from Packet import Packet
from openpgp.code import *

class CompressedData(Packet):
    __doc__ = """Compressed Data Packet
    """ + Packet._ivars

    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])    
        except IndexError:
            pass

    def fill_body(self, d):
        self.body = CompressedDataBody(d)


class CompressedDataBody:
    """Compressed Data

    :IVariables:
        - `alg`: integer compression algorithm code
        - `data`: decompressed data
        - `_d`: string of raw packet body data
        - `_comp_d`: string of compressed data (_d[1:])
    """
    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])    
        except IndexError:
            pass

    #def __getattr__(self, name):
        # I don't think that decompression is something that needs to be done
        # automatically.
    #    if 'data' == name:
    #        return self.__decompress()
    #    else:
    #        return self.__dict__[name]

    def fill(self, d):
        self._d = d
        self.alg = ord(d[0])
        self._comp_d = d[1:]
        self.data = self.decompress()

    def decompress(self):
        if COMP_UNCOMPRESSED == self.alg:
            data = self._comp_d
        # From 5.6: PGP2.6 uses 13 bits of compression ~ too bad
        elif COMP_ZIP == self.alg: # ..from zipfile.py source
            dc = zlib.decompressobj(-15)
            bytes = dc.decompress(self._comp_d)
            ex = dc.decompress('Z') + dc.flush()
            if ex:
                bytes = bytes + ex
            data = bytes
        elif COMP_ZLIB == self.alg:
            dc = zlib.decompressobj()
            data = dc.decompress(self._comp_d)
        # 100-110:Private/Experimental
        #elif self.alg in range(100, 111):
        #    raise NotImplementedError("Unsupported compression algorithm->(%s)" % (str(self.alg)))
        else:
            raise NotImplementedError("Unsupported compression algorithm->(%s)" % self.alg)
        return data

def create_CompressedDataBody(alg, d):
    """Create a CompressedDataBody instance.

    :Parameters:
        - `alg`: integer compressed algorithm constant
        - `d`: string data to compress

    :Returns: `CompressedDataBody` instance
    """
    if COMP_ZIP == alg: # ..from zipfile.py source
        cmpr = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION, zlib.DEFLATED, -15)
        data = cmpr.compress(d)
        ex = cmpr.flush()
        if ex:
            data = data + ex
    elif COMP_ZLIB == alg:
        cmpr = zlib.compressobj()
        data = cmpr.compress(d)
        ex = cmpr.flush()
        if ex:
            data = data + ex
    elif COMP_UNCOMPRESSED == alg:
        data = d
    else:
        raise NotImplementedError("Unsupported compression algorithm->(%s)" % alg)
    return CompressedDataBody(''.join([chr(alg), data]))
