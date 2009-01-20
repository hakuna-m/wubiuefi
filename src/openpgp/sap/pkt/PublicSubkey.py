"""Public subkey RFC 2440.5.5.1.2

Public subkey packets are just like public key packets, with one
difference: they are subkeys.
"""
from PublicKey import PublicKey, PublicKeyBody


class PublicSubkey(PublicKey):
    __doc__ = """Public Subkey Packet
    """ + PublicKey._ivars

    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])    
        except IndexError:
            pass

    def fill_body(self, d):
        self.body = PublicSubkeyBody(d)


class PublicSubkeyBody(PublicKeyBody):
    _title = """Public Subkey
    """
    _ivars = PublicKeyBody._ivars
    _notes = PublicKeyBody._notes 
    __doc__ = ''.join([_title, _ivars, _notes])
    # please excuse the __doc__ voodoo
    
    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])
        except IndexError:
            pass
