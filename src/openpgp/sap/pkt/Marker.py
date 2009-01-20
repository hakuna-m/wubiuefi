"""Marker RFC 2440.5.8

The marker packet is a dummy packet that must be ignored.

Move along.
"""
from Packet import Packet

class Marker(Packet):
    __doc__ = """Marker Packet
    """ + Packet._ivars

    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])    
        except IndexError:
            pass

    def fill_body(self, d):
        self.body = MarkerBody(d)


class MarkerBody:
    """Marker

    :IVariables:
        - `value`: three octets that spell 'PGP'
        - `_d`: string data comprising the body
    """
    
    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])
        except IndexError:
            pass

    def fill(self, d):
        self._d = self.value = d
