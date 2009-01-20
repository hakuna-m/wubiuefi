"""Modification detection code RFC 2440.5.14

The modification detection code contains a SHA-1 hash of the plaintext
in a decrypted symmetrically encrypted integrity protected packet.
"""
from Packet import Packet


class ModificationDetectionCode(Packet):
    __doc__ = """Modification Detection Code Packet
    """ + Packet._ivars

    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])    
        except IndexError:
            pass

    def __str__(self):
        return "<ModificationDetectionCode instance>"

    def fill_body(self, d):
        self.body = ModificationDetectionCodeBody(d)


class ModificationDetectionCodeBody:
    """Modification Detection Code

    :IVariables:
        - `hash`: string of 20 SHA-1 hashed octets
        - `_d`: string used to build packet body (same as `hash`)
    """

    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])    
        except IndexError:
            pass

    def fill(self, d):
        if len(d) == 20:
            self._d = self.hash = d
        else:
            raise PGPPacketError, "MDCode packet body must be 20 characters long, not->(%s)." % len(d)
