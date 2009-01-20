"""Symmetrically encrypted, integrity protected data RFC 2440.5.13

The symmetrically encrypted data packet holds symmetrically
encrypted data and a modification detection code
(`ModificationDetectionCode`) used packet to verify the intgrity of
the decrypted cleartext. It is left to the recipient to figure out how
to decrypt it (because, technically, a lone symmetrically encrypted,
integrity protected data packet defines a valid message).

Normally one or more session key packets (either symmetrically
encrypted or public key encrypted) precede the symmetrically encrypted,
integrity protected data packet. The session key packets specify the
symmetric algorithm used and hold the decryption key.

The modification detection code packet is hidden *inside* this
packet's body of data after the encryption target cleartext message
(which is, most likely, other packets)::

    |----symmetrically encrypted, integrity protected packet body-------|
    |--version--|-------------------encrypted data----------------------|
                |--cleartext message--|--modification detection packet--|
"""
from Packet import Packet

import openpgp.sap.util.strnum as STN

class SymmetricallyEncryptedIntegrityProtectedData(Packet):
    __doc__ = """Symmetrically Encrypted, Integrity Protected Data Packet 
    """ + Packet._ivars

    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])    
        except IndexError:
            pass

    def fill_body(self, d):
        self.body = SymmetricallyEncryptedIntegrityProtectedDataBody(d)

class SymmetricallyEncryptedIntegrityProtectedDataBody:
    """Symmetrically Encrypted, Integrity Protected Data

    :IVariables:
        - `version`: integer (should be 1)
        - `data`: string of encrypted data
        - `_d`: string of data used to build packet body
    """

    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])    
        except IndexError:
            pass

    def fill(self, d):
        self._d = d
        self.version = STN.str2int(d[0:1])
        self.data = d[1:]
