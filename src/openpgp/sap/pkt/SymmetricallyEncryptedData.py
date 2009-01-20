"""Symmetrically encrypted data RFC 2440.5.7

The symmetrically encrypted data packet just holds symmetrically
encrypted data - no header information or anything else. It is left
to the recipient to figure out how to decrypt it (because,
technically, a lone symmetrically encrypted data packet defines a
valid message).

Normally one or more session key packets (either symmetrically
encrypted or public key encrypted) precede the symmetrically encrypted
data packet. The session key packets specify the symmetric algorithm
used and hold the decryption key.
"""
from Packet import Packet

class SymmetricallyEncryptedData(Packet):
    __doc__ = """Symmetrically Encrypted Data Packet
    """ + Packet._ivars

    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])    
        except IndexError:
            pass

    def fill_body(self, d):
        self.body = SymmetricallyEncryptedDataBody(d)


class SymmetricallyEncryptedDataBody:
    """Symmetrically Encrypted Data

    :IVariables:
        - `data`: string of encrypted data
        - `_d`: string of data used to build body (in this case, the
          same as `data`)
    """

    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])    
        except IndexError:
            pass

    def fill(self, d):
        self._d = self.data = d
