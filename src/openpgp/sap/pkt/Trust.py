"""Trust RFC 2440.5.10

The trust packet holds information about a local user's degree of
trust over a key. Right now this packet is recognized but not used
for anything. Trust packets are not meant to be used outside a
user's personal OpenPGP implementation.
"""
from Packet import Packet

class Trust(Packet):
    __doc__ = """Trust Packet
    """ + Packet._ivars

    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])    
        except IndexError:
            pass

    def fill_body(self, d):
        self.body = TrustBody(d)

class TrustBody:
    """Trust

    :IVariables:
        - `_d`: string of data used to build body
    """
    
    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])    
        except IndexError:
            pass
    def fill(self, d):
        self._d = d
